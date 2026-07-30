"""investigate_canon.py — shared Unicode canonicalizer for the content checks.

Applied to the MATCH COPY only (the text the regex/classifier sees) — it NEVER rewrites the
artifact on disk. Defeats homoglyph / zero-width / fullwidth / combining-mark / RTL evasions
of the tier / register / temporal / label / diagnosis checks, while leaving legitimate
accented prose (cafe, naive, Muller, Greek/Cyrillic full words) ALLOWED — because the folded
copy is only ever fed to the sensitive ASCII-token regexes, and an accented word never folds
INTO a sensitive token.

Stages:
  canon(text)            NFKC fold + strip format chars (Cf, incl. zero-width / RTL marks /
                         BOM) + strip nonspacing combining marks (Mn).
  fold_confusables(text) additionally map known Latin-look-alike homoglyphs (Cyrillic / Greek)
                         to their ASCII letter, so 'T1' written with a Cyrillic T folds to
                         'T1' and the tier regex fires.
  match_copy(text)       = fold_confusables(canon(text))  — the form the checks should match.
  mixed_script_token(t)  narrow tripwire: first token mixing ASCII word-chars with a known
                         confusable (homoglyph-smuggle signature), else ''.
"""
import unicodedata
import re

# zero-width / bidi / format chars, by codepoint (kept as chr() so this source stays
# ASCII-clean). Most are category Cf and would be stripped anyway — this is belt+braces.
_ZW = "".join(chr(c) for c in (
    0x200b, 0x200c, 0x200d, 0x200e, 0x200f,
    0x2060, 0x2061, 0x2062, 0x2063, 0x2064,
    0xfeff, 0x00ad, 0x034f, 0x061c,
    0x202a, 0x202b, 0x202c, 0x202d, 0x202e,
    0x2066, 0x2067, 0x2068, 0x2069,
))

# Latin look-alikes that NFKC does NOT fold (Cyrillic / Greek), by codepoint -> ASCII.
_CONFUSABLES = {
    # Cyrillic lower
    0x0430: "a", 0x0435: "e", 0x043e: "o", 0x0440: "p", 0x0441: "c",
    0x0445: "x", 0x0443: "y", 0x0456: "i", 0x0458: "j", 0x0455: "s",
    0x043a: "k", 0x0501: "d", 0x04bb: "h", 0x0432: "v", 0x043c: "m",
    0x043d: "n", 0x0442: "t", 0x0431: "b",
    # Cyrillic upper
    0x0410: "A", 0x0415: "E", 0x041e: "O", 0x0420: "P", 0x0421: "C",
    0x0425: "X", 0x0423: "Y", 0x0406: "I", 0x041a: "K", 0x0412: "B",
    0x041c: "M", 0x041d: "H", 0x0422: "T",
    # Greek lower
    0x03bf: "o", 0x03b1: "a", 0x03bd: "v", 0x03c1: "p", 0x03b5: "e",
    0x03c4: "t", 0x03b9: "i", 0x03ba: "k", 0x03c5: "u",
    # Greek upper
    0x0399: "I", 0x039f: "O", 0x03a1: "P", 0x03a4: "T", 0x0391: "A",
    0x0392: "B", 0x0395: "E", 0x0397: "H", 0x039a: "K", 0x039c: "M",
    0x039d: "N", 0x03a7: "X", 0x0396: "Z",
    # same-(Latin)-script look-alikes NFKC does not fold (M1)
    0x0261: "g", 0x0269: "i", 0x026a: "i", 0x0274: "n", 0x1d04: "c",
    0x1d07: "e", 0x04cf: "l", 0x0578: "n", 0x0585: "o",
}


def canon(text):
    if not text:
        return text
    t = unicodedata.normalize("NFKC", text)
    out = []
    for ch in t:
        if ch in _ZW:
            continue
        cat = unicodedata.category(ch)
        if cat == "Cf" or cat == "Mn":
            continue
        out.append(ch)
    return "".join(out)


def fold_confusables(text):
    if not text:
        return text
    return "".join(_CONFUSABLES.get(ord(ch), ch) for ch in text)


def match_copy(text):
    """The canonical match form the content checks should run their regexes against."""
    return fold_confusables(canon(text))


_TOKEN = re.compile(r"[^\W_]*[^\x00-\x7f][^\W_]*", re.UNICODE)


_NONLATIN_SCRIPTS = ("CYRILLIC", "GREEK", "ARMENIAN", "COPTIC", "CHEROKEE", "GEORGIAN")


def _is_nonlatin_letter(ch):
    if ord(ch) < 128 or not ch.isalpha():
        return False
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return False
    return any(name.startswith(p) for p in _NONLATIN_SCRIPTS)


def mixed_script_token(text):
    """First token that mixes ASCII-Latin word-chars with EITHER a curated Latin-script
    look-alike OR any non-Latin-script letter (Cyrillic/Greek/Armenian/...). This is the
    homoglyph-smuggle signature and is no longer limited to the ~curated dict (M1). Pure
    non-Latin words and legitimately accented Latin words (cafe, Muller, naive) are NOT
    flagged, because their non-ASCII letters are Latin-script and not curated confusables."""
    if not text:
        return ""
    for m in _TOKEN.finditer(text):
        tok = m.group(0)
        has_ascii_latin = any(("a" <= c.lower() <= "z") for c in tok if ord(c) < 128)
        if not has_ascii_latin:
            continue
        if any(ord(c) in _CONFUSABLES for c in tok) or any(_is_nonlatin_letter(c) for c in tok):
            return tok
    return ""


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "match"
    data = sys.stdin.read()
    if mode == "canon":
        sys.stdout.write(canon(data))
    elif mode == "mixed":
        sys.stdout.write(mixed_script_token(data))
    else:
        sys.stdout.write(match_copy(data))
