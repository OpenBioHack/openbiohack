#!/bin/bash
# convert-source.sh — bundled conversion/OCR helper for the extract-health-data skill.
#
# Turns one raw health-record source (or a whole directory) into plain text staged for
# Phase A extraction, choosing the right tool per file type and falling back to OCR for
# scanned PDFs/images. This exists so no investigation run hand-rolls the conversion loop
# inline (root-cause fix: the skill describes the loop in prose; this *is* the loop).
#
# It only CONVERTS. It never interprets, summarises, or drops content. The converted .txt
# is itself an artifact, tagged with a provenance header, to be verified against the
# original during Phase A (verbatim originals remain canonical).
#
# Usage:
#   convert-source.sh <source-file-or-dir> <output-dir> [--ocr-threshold N] [--dpi N]
#
#   <source-file-or-dir>  a single file, or a directory processed recursively
#   <output-dir>          where .txt outputs are written (created if absent)
#   --ocr-threshold N     pdftotext char-count below which a PDF is treated as scanned
#                         and sent to OCR (default 1200)
#   --dpi N               rasterisation DPI for OCR (default 300)
#
# Per-file behaviour:
#   *.pdf   PyMuPDF word-level (+positions), else pdftotext -layout. If output < threshold
#           chars OR pdf is encrypted, escalate:
#           - encrypted: try `qpdf --decrypt` (empty pw), else record ENCRYPTED.
#           - low-text (scanned): OCR via pdftoppm (DPI) + tesseract, page by page,
#             each page delimited by "===== PAGE n =====".
#   *.png/*.jpg/*.jpeg/*.tif/*.tiff   tesseract OCR.
#   *.rtf/*.doc/*.docx   textutil -convert txt (macOS native).
#   *.xlsx   stdlib-python xlsx->tsv (zipfile + xml; no external deps).
#   *.csv/*.tsv/*.txt/*.md   copied through verbatim.
#   *.pages/*.numbers/*.key   Apple iWork — try to pull the embedded PDF preview
#           (QuickLook/zip), else record NO-PLUGIN (needs proprietary software).
#   *.zip   listed only (a manifest, role=container-manifest); contents not auto-expanded.
#   other   record NO-PLUGIN naming the unhandled type.
#
# EVERY source gets exactly one record in <output-dir>/conversion-report.json. A source is
# only marked `converted` if its output survives a content check the converter cannot fake:
#   - paged sources (OCR'd PDFs): pages produced must equal the page count `pdfinfo` reports
#     for the ORIGINAL, and each page must carry a real content token. An OCR run that emits
#     27 page-delimiters and zero words fails; it does not silently pass.
#   - everything else: the body (minus the provenance header) must carry a content token.
# Any source that is not `converted` makes this script exit NON-ZERO, so a caller cannot
# proceed with a hole in the data. Failure statuses are deliberately distinct:
#   blocked-environment  the machine is missing a tool / cannot write scratch  -> fix the box
#   no-plugin            we have no converter for this format                  -> write one
#   failed               a converter ran and produced nothing usable           -> investigate
#
# Scratch lives under <output-dir>/.work (NOT mktemp): the output dir is provably writable,
# and a sandboxed/locked-down $TMPDIR previously caused OCR to produce empty files silently.
#
# Required for full coverage: pdftotext, pdfinfo, pdftoppm, tesseract (poppler + tesseract
# via Homebrew), textutil (macOS), qpdf (optional, encrypted PDFs), python3 (xlsx).
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" && pwd)"

OCR_THRESHOLD=1200
DPI=300
SRC=""
OUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --ocr-threshold) OCR_THRESHOLD="$2"; shift 2;;
    --dpi) DPI="$2"; shift 2;;
    *) if [ -z "$SRC" ]; then SRC="$1"; elif [ -z "$OUT" ]; then OUT="$1"; fi; shift;;
  esac
done

if [ -z "$SRC" ] || [ -z "$OUT" ]; then
  echo "usage: convert-source.sh <source-file-or-dir> <output-dir> [--ocr-threshold N] [--dpi N]" >&2
  exit 2
fi
mkdir -p "$OUT" || { echo "FATAL: output dir not writable: $OUT" >&2; exit 3; }
WORK="$OUT/.work"
rm -rf "$WORK"; mkdir -p "$WORK" || { echo "FATAL: scratch not writable: $WORK" >&2; exit 3; }
RECORDS="$WORK/records.jsonl"; : > "$RECORDS"

have() { command -v "$1" >/dev/null 2>&1; }
# slugify a path relative to the source root into a flat filename. Keeps the directory
# component (source trees can nest several levels deep) so two files sharing a basename cannot collide.
slug() {
  local rel="${1#"$SRC"/}"
  echo "$rel" | sed 's#^\./##; s#/#__#g; s/ /_/g'
}

jesc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

# record <source> <status> <tool> <declared> <produced> <reason>
record() {
  printf '{"source":"%s","status":"%s","role":"%s","tool":"%s","declared":%s,"produced":%s,"reason":"%s","output":"%s"}\n' \
    "$(jesc "$1")" "$2" "${ROLE:-document}" "$(jesc "$3")" "${4:-null}" "${5:-null}" "$(jesc "${6:-}")" "$(jesc "${7:-}")" >> "$RECORDS"
}

fail() { # source, status, reason
  record "$1" "$2" "" null null "$3" ""
  echo "  -> [$2] $1 — $3"
}

# A body carries real content if it has a word (3+ letters) or a number (2+ digits),
# ignoring our own provenance header and page delimiters. Guards against a converter
# that exits 0 having produced only structure.
# NB: deliberately NOT `... | grep -q`. Under `set -o pipefail`, grep -q exits on the first
# match, SIGPIPEs the upstream grep, and the pipeline reports failure — i.e. it would report
# "no content" precisely BECAUSE content was found early. grep -c consumes the whole stream.
content_ok() {
  local n
  n="$(grep -vE '^<<<|^===== (PAGE|SHEET)' "$1" 2>/dev/null | grep -cE '[A-Za-z]{3}|[0-9]{2}')"
  [ "${n:-0}" -gt 0 ]
}

pdf_pages() { pdfinfo "$1" 2>/dev/null | awk '/^Pages:/{print $2; exit}'; }

# Promote a converted body into place, but only if it carries content.
# finalize <source> <tool> <body-file> <dest-txt> [declared] [produced]
finalize() {
  local f="$1" tool="$2" body="$3" txt="$4" decl="${5:-null}" prod="${6:-null}"
  if [ ! -s "$body" ] || ! content_ok "$body"; then
    rm -f "$txt"
    fail "$f" "failed" "$tool ran but produced no readable content"
    return 1
  fi
  { provenance "$f" "$tool"; cat "$body"; } > "$txt"
  record "$f" "converted" "$tool" "$decl" "$prod" "" "$txt"
  return 0
}

provenance() { # original-path, tool
  echo "<<<CONVERTED ARTIFACT — original is canonical>>>"
  echo "<<<source: $1>>>"
  echo "<<<tool: $2>>>"
  echo ""
}

xlsx_to_tsv() { # xlsx, outpath  -> non-zero on failure (does NOT swallow its own error)
python3 - "$1" "$2" <<'PY'
import sys, zipfile, re
from xml.etree import ElementTree as ET
xlsx, out = sys.argv[1], sys.argv[2]
ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
try:
    z = zipfile.ZipFile(xlsx)
except Exception as e:
    print(f"xlsx open failed: {e}", file=sys.stderr); sys.exit(1)
shared=[]
if 'xl/sharedStrings.xml' in z.namelist():
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.iter(ns+'si'):
        shared.append(''.join(t.text or '' for t in si.iter(ns+'t')))
sheets=sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$', n))
if not sheets:
    print("xlsx has no worksheets", file=sys.stderr); sys.exit(1)
def colnum(ref):
    m=re.match(r'([A-Z]+)',ref or '')
    if not m: return 0
    n=0
    for c in m.group(1): n=n*26+(ord(c)-64)
    return n-1
with open(out,'w') as f:
    for sh in sheets:
        f.write(f"===== SHEET: {sh} =====\n")
        root=ET.fromstring(z.read(sh))
        for row in root.iter(ns+'row'):
            cells={}
            maxc=0
            for c in row.findall(ns+'c'):
                idx=colnum(c.get('r'))
                t=c.get('t'); v=c.find(ns+'v'); val=''
                if v is not None and v.text is not None:
                    val = shared[int(v.text)] if t=='s' and v.text.isdigit() else v.text
                isn=c.find(ns+'is')
                if isn is not None:
                    val=''.join(x.text or '' for x in isn.iter(ns+'t'))
                cells[idx]=val; maxc=max(maxc,idx)
            f.write('\t'.join(cells.get(i,'') for i in range(maxc+1))+'\n')
print(len(sheets))
PY
}

ocr_pdf() { # path, base, txt  — page-corresponding OCR; fails loudly, never silently empty
  local f="$1" base="$2" txt="$3" w declared n=0 valid=0 img
  w="$WORK/$base"; rm -rf "$w"
  if ! mkdir -p "$w"; then
    fail "$f" "blocked-environment" "cannot create scratch dir $w"
    return 1
  fi
  if ! have pdftoppm || ! have tesseract; then
    fail "$f" "blocked-environment" "scanned PDF needs pdftoppm + tesseract; not installed"
    return 1
  fi
  # rasterise PLAIN_SRC when set (a decrypted copy in scratch); else the original path.
  local raster="${PLAIN_SRC:-$f}"
  declared="$(pdf_pages "$raster")"; declared="${declared:-0}"
  pdftoppm -r "$DPI" -png "$raster" "$w/pg" >/dev/null 2>&1
  local body="$w/ocr.txt"; : > "$body"
  for img in "$w"/pg*.png; do
    [ -e "$img" ] || break
    n=$((n+1))
    echo "===== PAGE $n =====" >> "$body"
    tesseract "$img" stdout >> "$body" 2>/dev/null
  done
  if [ "$n" -eq 0 ]; then
    fail "$f" "blocked-environment" "pdftoppm rasterised 0 of $declared pages (scratch or tool problem)"
    return 1
  fi
  # count pages that carry REAL content — not just a delimiter the converter itself emitted
  valid="$(awk '/^===== PAGE /{p++; next} p>0 && /[A-Za-z][A-Za-z][A-Za-z]|[0-9][0-9]/{seen[p]=1}
                END{v=0; for (i in seen) v++; print v+0}' "$body")"
  if [ "$declared" -gt 0 ] && [ "$valid" -ne "$declared" ]; then
    fail "$f" "failed" "OCR page mismatch: pdfinfo declares $declared pages, only $valid produced readable text"
    return 1
  fi
  finalize "$f" "pdftoppm ${DPI}dpi + tesseract OCR" "$body" "$txt" "$declared" "$valid"
}

# Decrypt an encrypted PDF into scratch. Tries, in order: empty password; any password in
# $PDF_PASSWORD; then the targeted recoverer (health-portal PDFs are locked with the patient
# DOB/name — pass hints via $PDF_DOB (DDMMYYYY) / $PDF_NAME). Echoes the decrypted path on
# success. The password is used in-process only: never recorded, never printed.
decrypt_pdf() { # src, base -> echoes decrypted path, or nothing
  local f="$1" base="$2" pw
  local dec="$WORK/$base.decrypted.pdf"
  have qpdf || return 1
  # NB --warning-exit-0: qpdf exits 3 on warnings (e.g. "object has offset 0"), which are
  # cosmetic and still produce a valid file. Without this, a decryptable PDF reads as failed.
  _try_qpdf() { # password
    rm -f "$dec" 2>/dev/null
    qpdf --warning-exit-0 --password="$1" --decrypt "$f" "$dec" >/dev/null 2>&1
    [ -s "$dec" ]
  }
  for pw in "" ${PDF_PASSWORD:+"$PDF_PASSWORD"}; do
    if _try_qpdf "$pw"; then echo "$dec"; return 0; fi
  done
  if have python3 && [ -f "$SCRIPT_DIR/pdf-unlock.py" ]; then
    local -a hints=()
    [ -n "${PDF_DOB:-}" ] && hints+=(--dob "$PDF_DOB")
    [ -n "${PDF_NAME:-}" ] && hints+=(--name "$PDF_NAME")
    pw="$(python3 "$SCRIPT_DIR/pdf-unlock.py" "$f" "${hints[@]}" 2>/dev/null)"
    if [ -n "$pw" ] && _try_qpdf "$pw"; then echo "$dec"; return 0; fi
  fi
  return 1
}

# Convert an already-openable PDF through the normal text→OCR ladder and finalize to <txt>.
# <label-src> is the path used for provenance/records (the original, even when <pdf> is a
# decrypted copy in scratch).
convert_plain_pdf() { # pdf, label-src, txt, tag
  local pdf="$1" f="$2" txt="$3" tag="$4" base declared cnt
  base="$(slug "$f")"; declared="$(pdf_pages "$pdf")"; declared="${declared:-null}"
  if have python3 && [ -f "$SCRIPT_DIR/convert-pdf-fitz.py" ] \
     && python3 "$SCRIPT_DIR/convert-pdf-fitz.py" "$pdf" "$WORK/$base.body" \
          --pos "$OUT/$base.pos.json" --min-chars "$OCR_THRESHOLD" 2>/dev/null; then
    finalize "$f" "${tag}PyMuPDF (fitz) word-level +positions" "$WORK/$base.body" "$txt" "$declared" null \
      && echo "  -> [pdf/fitz+pos] $f"
    return
  fi
  pdftotext -layout "$pdf" "$WORK/$base.body" 2>/dev/null
  cnt=$(wc -c < "$WORK/$base.body" 2>/dev/null | tr -d ' '); cnt=${cnt:-0}
  if [ "$cnt" -lt "$OCR_THRESHOLD" ]; then
    PLAIN_SRC="$pdf" ocr_pdf "$f" "$base" "$txt" && echo "  -> [pdf/OCR] $f"
  else
    finalize "$f" "${tag}pdftotext -layout" "$WORK/$base.body" "$txt" "$declared" null \
      && echo "  -> [pdf/text] $f"
  fi
}

convert_pdf() { # path
  local f="$1" base txt enc dec
  base="$(slug "$f")"; txt="$OUT/$base.txt"
  enc="$(pdfinfo "$f" 2>&1 | grep -ic 'Incorrect password')"
  if [ "$enc" -gt 0 ]; then
    dec="$(decrypt_pdf "$f" "$base")"
    if [ -n "$dec" ] && [ -f "$dec" ]; then
      # decrypted copy may be scanned (image-only) — route through the FULL text→OCR ladder
      convert_plain_pdf "$dec" "$f" "$txt" "qpdf --decrypt + "
    else
      fail "$f" "blocked-environment" "password-protected; no empty/supplied/derivable password worked. Provide it via PDF_PASSWORD, or a DOB hint via PDF_DOB=DDMMYYYY."
    fi
    return
  fi
  convert_plain_pdf "$f" "$f" "$txt" ""
}

convert_one() { # path
  local f="$1" ext lc base txt sheets
  ROLE="document"
  ext="${f##*.}"; lc="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  base="$(slug "$f")"; txt="$OUT/$base.txt"
  case "$lc" in
    pdf) convert_pdf "$f";;
    png|jpg|jpeg|tif|tiff)
      if have tesseract; then
        tesseract "$f" stdout > "$WORK/$base.body" 2>/dev/null
        finalize "$f" "tesseract OCR" "$WORK/$base.body" "$txt" 1 1 && echo "  -> [image/OCR] $f"
      else fail "$f" "blocked-environment" "image OCR needs tesseract"; fi;;
    heic|heif)
      # Apple HEIC/HEIF (iPhone photos). Decode to PNG then OCR. Prefer the pinned pillow-heif venv
      # (writes ONLY to explicit paths → sandbox-safe); fall back to macOS `sips` (needs the Darwin
      # per-user temp, which a sandbox may block). If NEITHER decoder works here, CATALOGUE the image
      # (present on disk, role=image-undecoded, not OCR'd) instead of failing — an image we cannot
      # decode must not halt the whole run. Documents that fail still halt (the no-hole guarantee).
      if [ -x "$SCRIPT_DIR/heic-venv/bin/python3" ] && [ -f "$SCRIPT_DIR/heic-to-png.py" ] && have tesseract \
         && "$SCRIPT_DIR/heic-venv/bin/python3" "$SCRIPT_DIR/heic-to-png.py" "$f" "$WORK/$base.png" >/dev/null 2>&1 \
         && [ -s "$WORK/$base.png" ]; then
        tesseract "$WORK/$base.png" stdout > "$WORK/$base.body" 2>/dev/null
        finalize "$f" "pillow-heif heic->png + tesseract OCR" "$WORK/$base.body" "$txt" 1 1 && echo "  -> [heic/OCR] $f"
      elif have sips && have tesseract && sips -s format png "$f" --out "$WORK/$base.png" >/dev/null 2>&1 && [ -s "$WORK/$base.png" ]; then
        tesseract "$WORK/$base.png" stdout > "$WORK/$base.body" 2>/dev/null
        finalize "$f" "sips heic->png + tesseract OCR" "$WORK/$base.body" "$txt" 1 1 && echo "  -> [heic/OCR] $f"
      else
        ROLE="image-undecoded"
        record "$f" "catalogued" "" null null "HEIC/HEIF not decodable in this environment (no pillow-heif in venv; sips temp blocked) — catalogued on disk, not OCR'd" ""
        echo "  -> [heic/catalogued — not decodable here] $f"
      fi;;
    rtf|doc|docx)
      if have textutil; then
        textutil -convert txt "$f" -stdout > "$WORK/$base.body" 2>/dev/null
        finalize "$f" "textutil" "$WORK/$base.body" "$txt" 1 1 && echo "  -> [doc] $f"
      else fail "$f" "blocked-environment" "needs macOS textutil"; fi;;
    xlsx)
      if have python3; then
        if sheets="$(xlsx_to_tsv "$f" "$WORK/$base.body" 2>/dev/null)"; then
          finalize "$f" "python3 xlsx->tsv" "$WORK/$base.body" "$txt" "$sheets" "$sheets" \
            && echo "  -> [xlsx ${sheets}sh] $f"
        else
          fail "$f" "failed" "xlsx could not be parsed (corrupt, or not a real xlsx)"
        fi
      else fail "$f" "blocked-environment" "xlsx needs python3"; fi;;
    csv|tsv|txt|md)
      cp "$f" "$WORK/$base.body" 2>/dev/null
      finalize "$f" "copy" "$WORK/$base.body" "$txt" 1 1 && echo "  -> [text/copy] $f";;
    pages|numbers|key)
      local w="$WORK/$base.iwork"; mkdir -p "$w"
      # (1) legacy '09 bundles embed a full PDF at QuickLook/Preview.pdf — lift it if present
      if unzip -o -j "$f" '*Preview.pdf' -d "$w" >/dev/null 2>&1; then
        local pv; pv="$(ls "$w"/*.pdf 2>/dev/null | head -1)"
        if [ -n "$pv" ]; then
          pdftotext -layout "$pv" "$w/body" 2>/dev/null
          if [ -s "$w/body" ] && content_ok "$w/body"; then
            finalize "$f" "iWork QuickLook preview + pdftotext" "$w/body" "$txt" \
              "$(pdf_pages "$pv")" null && echo "  -> [iwork/preview] $f"
            return
          fi
        fi
      fi
      # (2) modern IWA bundles: decode Index/*.iwa (Snappy+protobuf) directly — no app needed
      if have python3 && [ -f "$SCRIPT_DIR/convert-iwork.py" ] \
         && python3 "$SCRIPT_DIR/convert-iwork.py" "$f" "$w/body" 2>/dev/null \
         && [ -s "$w/body" ] && content_ok "$w/body"; then
        finalize "$f" "iWork IWA (snappy+protobuf) text" "$w/body" "$txt" 1 1 \
          && echo "  -> [iwork/iwa] $f"
        return
      fi
      # (3) last resort: OCR the bundle's embedded preview.jpg (full-page raster)
      if unzip -o -j "$f" 'preview.jpg' -d "$w" >/dev/null 2>&1 && [ -f "$w/preview.jpg" ] \
         && have tesseract; then
        tesseract "$w/preview.jpg" stdout > "$w/body" 2>/dev/null
        if [ -s "$w/body" ] && content_ok "$w/body"; then
          finalize "$f" "iWork preview.jpg + tesseract OCR" "$w/body" "$txt" 1 1 \
            && echo "  -> [iwork/preview-ocr] $f"
          return
        fi
      fi
      fail "$f" "no-plugin" "Apple iWork file: no PDF preview, IWA text decode empty, and no OCR-able preview. Export it to PDF/CSV from Pages/Numbers.";;
    zip)
      ROLE="container-manifest"
      { echo "# ZIP manifest (contents not auto-expanded):"; unzip -l "$f" 2>/dev/null; } > "$WORK/$base.body"
      txt="$OUT/$base.manifest.txt"
      finalize "$f" "unzip -l (manifest only)" "$WORK/$base.body" "$txt" 1 1 \
        && echo "  -> [zip/manifest] $f";;
    *) fail "$f" "no-plugin" "unhandled file type .$lc — no converter exists for this format yet";;
  esac
}

echo "convert-source: src=$SRC out=$OUT ocr-threshold=$OCR_THRESHOLD dpi=$DPI"
for t in pdftotext pdfinfo pdftoppm tesseract textutil qpdf python3; do
  have "$t" && echo "  tool OK: $t" || echo "  tool MISSING: $t"
done
echo "---"
if [ -d "$SRC" ]; then
  SRC="${SRC%/}"
  while IFS= read -r -d '' f; do convert_one "$f"; done \
    < <(find -L "$SRC" -type f ! -name '.DS_Store' ! -path '*/.work/*' -print0)
else
  # single-file mode: the slug is relative to the file's own directory
  ONE="$SRC"; SRC="$(dirname "$SRC")"; convert_one "$ONE"
fi

# ── receipt ────────────────────────────────────────────────────────────────────────────
TOTAL=$(wc -l < "$RECORDS" | tr -d ' ')
OKC=$(grep -c '"status":"converted"' "$RECORDS" || true)
BADC=$((TOTAL - OKC))
{
  echo '{'
  echo "  \"summary\": {\"total\": $TOTAL, \"converted\": $OKC, \"failed\": $BADC},"
  echo '  "records": ['
  sed '$!s/$/,/' "$RECORDS" | sed 's/^/    /'
  echo '  ]'
  echo '}'
} > "$OUT/conversion-report.json"

echo "---"
echo "converted $OKC/$TOTAL   report: $OUT/conversion-report.json"
if [ "$BADC" -gt 0 ]; then
  echo ""
  echo "!! $BADC source(s) did NOT convert. The run must not proceed with a hole in the data:"
  grep -v '"status":"converted"' "$RECORDS" \
    | sed 's/.*"source":"\([^"]*\)".*"status":"\([^"]*\)".*"reason":"\([^"]*\)".*/  [\2] \1\n        \3/'
  exit 1
fi
rm -rf "$WORK"
exit 0
