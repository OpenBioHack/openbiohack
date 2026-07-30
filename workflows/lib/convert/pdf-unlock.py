#!/usr/bin/env python3
"""pdf-unlock.py — recover the user password of a Standard-security PDF, print it, exit 0.

Health-portal PDFs (LabCorp, Vibrant, Quest, NHS) are almost always locked with the
patient's own date of birth or name — a *targeted* guess space of a few hundred strings,
not a brute force. This checks candidates in pure Python: the /U verification for R>=3 uses
MD5 + RC4 regardless of whether the streams are RC4 or AES, so no third-party crypto and no
network are needed to TEST a candidate.

Usage:
  pdf-unlock.py FILE [--dob DDMMYYYY] [--name NAME] [--extra pw1,pw2,...]
Prints the recovered password to stdout and exits 0 on success; exits 1 if none matched.
Nothing is written to disk and the password is never logged — the caller captures stdout.
"""
import re
import sys
import hashlib
import struct
import argparse

PAD = bytes([
    0x28,0xBF,0x4E,0x5E,0x4E,0x75,0x8A,0x41,0x64,0x00,0x4E,0x56,0xFF,0xFA,0x01,0x08,
    0x2E,0x2E,0x00,0xB6,0xD0,0x68,0x3E,0x80,0x2F,0x0C,0xA9,0xFE,0x64,0x53,0x69,0x7A])


def rc4(key: bytes, data: bytes) -> bytes:
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    out = bytearray()
    i = j = 0
    for ch in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(ch ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out)


def parse_string(body: bytes, key: bytes):
    """Return the bytes of /key as a PDF string: <hex> or (literal with escapes)."""
    mh = re.search(key + rb'\s*<([0-9A-Fa-f\s]+)>', body)
    if mh:
        return bytes.fromhex(re.sub(rb'\s', b'', mh.group(1)).decode())
    ml = re.search(key + rb'\s*\(', body)
    if not ml:
        return None
    i = ml.end()
    out = bytearray()
    depth = 1
    esc = {b'n': 10, b'r': 13, b't': 9, b'b': 8, b'f': 12}
    while i < len(body) and depth:
        c = body[i:i+1]
        if c == b'\\':
            nxt = body[i+1:i+2]
            if nxt in esc:
                out.append(esc[nxt]); i += 2
            elif nxt in (b'(', b')', b'\\'):
                out.append(nxt[0]); i += 2
            elif nxt.isdigit():
                oct_ = body[i+1:i+4]
                m = re.match(rb'[0-7]{1,3}', oct_)
                out.append(int(m.group(0), 8) & 0xFF); i += 1 + len(m.group(0))
            else:
                i += 2
        elif c == b'(':
            depth += 1; out.append(40); i += 1
        elif c == b')':
            depth -= 1
            if depth:
                out.append(41)
            i += 1
        else:
            out.append(c[0]); i += 1
    return bytes(out)


def compute_key(pw: bytes, O: bytes, P: int, id0: bytes, keylen: int,
                r: int, encrypt_metadata: bool) -> bytes:
    padded = (pw + PAD)[:32]
    h = hashlib.md5()
    h.update(padded)
    h.update(O[:32])
    h.update(struct.pack('<i', P))
    h.update(id0)
    if r >= 4 and not encrypt_metadata:
        h.update(b'\xff\xff\xff\xff')
    key = h.digest()
    if r >= 3:
        for _ in range(50):
            key = hashlib.md5(key[:keylen]).digest()
    return key[:keylen]


def user_pw_ok(pw: bytes, O, U, P, id0, keylen, r, enc_meta) -> bool:
    key = compute_key(pw, O, P, id0, keylen, r, enc_meta)
    if r == 2:
        return rc4(key, PAD) == U[:32]
    # R>=3: U = RC4 over MD5(PAD+ID0), then 19 re-keyed rounds; compare first 16 bytes
    h = hashlib.md5(); h.update(PAD); h.update(id0)
    val = h.digest()
    val = rc4(key, val)
    for i in range(1, 20):
        rk = bytes(b ^ i for b in key)
        val = rc4(rk, val)
    return val[:16] == U[:16]


def dob_variants(dob: str) -> list[str]:
    """dob is DDMMYYYY (8 digits). Emit the formats health portals actually use."""
    m = re.fullmatch(r'(\d{2})(\d{2})(\d{4})', dob)
    if not m:
        return []
    d, mo, y = m.groups()
    yy = y[2:]
    di, mi = str(int(d)), str(int(mo))  # unpadded
    out = [
        f"{d}{mo}{y}", f"{mo}{d}{y}", f"{y}{mo}{d}", f"{y}{d}{mo}",
        f"{d}-{mo}-{y}", f"{mo}-{d}-{y}", f"{y}-{mo}-{d}",
        f"{d}/{mo}/{y}", f"{mo}/{d}/{y}", f"{y}/{mo}/{d}", f"{d}.{mo}.{y}",
        f"{d}{mo}{yy}", f"{mo}{d}{yy}", f"{yy}{mo}{d}",
        f"{di}-{mi}-{y}", f"{di}/{mi}/{y}", f"{di}{mi}{y}", f"{di}{mi}{yy}", y,
    ]
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); uniq.append(s)
    return uniq


def name_variants(name: str) -> list[str]:
    parts = [p for p in re.split(r'\s+', name.strip()) if p]
    cased = set()
    for p in parts + ["".join(parts), "".join(reversed(parts))]:
        for v in (p, p.lower(), p.upper(), p.capitalize()):
            cased.add(v)
    return [c for c in cased if c]


def build_candidates(dob: str | None, name: str | None, extra: list[str]) -> list[str]:
    cands: list[str] = [""]
    cands += list(extra)
    if dob:
        cands += dob_variants(dob)
    if name:
        nv = name_variants(name)
        cands += nv
        if dob and re.fullmatch(r'\d{8}', dob):
            y = dob[4:]
            for n in nv:
                cands += [n + y, n + dob, n + "1", n + "123"]
    cands += ["password", "Password", "1234", "12345678", "0000",
              "changeme", "welcome", "test"]
    seen, out = set(), []
    for c in cands:
        if c not in seen:
            seen.add(c); out.append(c)
    return out


def find_encrypt_params(raw: bytes):
    enc = re.search(rb'/Encrypt\s+(\d+)\s+\d+\s+R', raw)
    body = raw
    if enc:
        num = enc.group(1)
        obj = re.search(num + rb'\s+0\s+obj(.*?)endobj', raw, re.S)
        if obj:
            body = obj.group(1)
    O = parse_string(body, b'/O')
    U = parse_string(body, b'/U')
    P = int(re.search(rb'/P\s+(-?\d+)', body).group(1))
    keylen = int(re.search(rb'/Length\s+(\d+)', body).group(1)) // 8
    r = int(re.search(rb'/R\s+(\d+)', body).group(1))
    enc_meta = b'/EncryptMetadata false' not in body
    id0 = bytes.fromhex(re.search(rb'/ID\s*\[\s*<([0-9A-Fa-f]+)>', raw).group(1).decode())
    return O, U, P, id0, keylen, r, enc_meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--dob", default=None, help="date of birth as DDMMYYYY")
    ap.add_argument("--name", default=None)
    ap.add_argument("--extra", default="", help="comma-separated extra candidates")
    args = ap.parse_args()

    raw = open(args.pdf, 'rb').read()
    try:
        O, U, P, id0, keylen, r, enc_meta = find_encrypt_params(raw)
    except Exception:
        return 1

    extra = [x for x in args.extra.split(",") if x] if args.extra else []
    for cand in build_candidates(args.dob, args.name, extra):
        if user_pw_ok(cand.encode('latin-1', 'ignore'), O, U, P, id0, keylen, r, enc_meta):
            sys.stdout.write(cand)  # password only, no newline, nothing else
            return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
