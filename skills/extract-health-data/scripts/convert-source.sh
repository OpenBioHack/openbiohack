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
#   *.pdf   pdftotext -layout. If output < threshold chars OR pdf is encrypted, escalate:
#           - encrypted: try `qpdf --decrypt` (empty pw), else emit a .ENCRYPTED marker.
#           - low-text (scanned): OCR via pdftoppm (DPI) + tesseract, page by page,
#             each page delimited by "===== PAGE n =====".
#   *.png/*.jpg/*.jpeg/*.tif/*.tiff   tesseract OCR.
#   *.rtf/*.doc/*.docx   textutil -convert txt (macOS native).
#   *.xlsx   stdlib-python xlsx->tsv (zipfile + xml; no external deps).
#   *.csv/*.tsv/*.txt/*.md   copied through verbatim.
#   *.pages/*.numbers/*.key   Apple iWork — try to pull the embedded PDF preview
#           (QuickLook/zip), else emit a .ESCALATE marker (needs proprietary software).
#   *.zip   listed only (a manifest .txt); contents not auto-expanded (e.g. genetics raw).
#   other   emit a .ESCALATE marker naming the unhandled type.
#
# Tooling is checked up front; a missing tool produces an explicit .TOOL-MISSING marker
# for that file rather than a silent skip. Required for full coverage: pdftotext, pdfinfo,
# pdftoppm, tesseract (poppler + tesseract via Homebrew), textutil (macOS), qpdf
# (optional, only for encrypted PDFs), python3 (xlsx).
set -uo pipefail

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
mkdir -p "$OUT"

have() { command -v "$1" >/dev/null 2>&1; }
# slugify a relative path into a flat filename
slug() { echo "$1" | sed 's#^\./##; s#/#__#g; s/ /_/g'; }

emit_marker() { # file, suffix, message
  local out; out="$OUT/$(slug "$1").$2"
  { echo "# CONVERSION MARKER: $2"; echo "# source: $1"; echo "# $3"; } > "$out"
  echo "  -> [$2] $1"
}

provenance() { # original-path, tool
  echo "<<<CONVERTED ARTIFACT — original is canonical>>>"
  echo "<<<source: $1>>>"
  echo "<<<tool: $2>>>"
  echo ""
}

xlsx_to_tsv() { # xlsx, outpath
python3 - "$1" "$2" <<'PY'
import sys, zipfile, re
from xml.etree import ElementTree as ET
xlsx, out = sys.argv[1], sys.argv[2]
ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
try:
    z = zipfile.ZipFile(xlsx)
except Exception as e:
    open(out,'w').write(f"# xlsx open failed: {e}\n"); sys.exit(0)
shared=[]
if 'xl/sharedStrings.xml' in z.namelist():
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.iter(ns+'si'):
        shared.append(''.join(t.text or '' for t in si.iter(ns+'t')))
sheets=sorted(n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$', n))
def colnum(ref):
    m=re.match(r'([A-Z]+)',ref or '');
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
PY
}

convert_pdf() { # path
  local f="$1" base txt cnt enc
  base="$(slug "$f")"; txt="$OUT/$base.txt"
  enc="$(pdfinfo "$f" 2>&1 | grep -ic 'Incorrect password')"
  if [ "$enc" -gt 0 ]; then
    if have qpdf && qpdf --decrypt "$f" "$OUT/$base.decrypted.pdf" >/dev/null 2>&1; then
      pdftotext -layout "$OUT/$base.decrypted.pdf" "$txt" 2>/dev/null
      { provenance "$f" "qpdf --decrypt + pdftotext"; cat "$txt"; } > "$txt.tmp" && mv "$txt.tmp" "$txt"
      echo "  -> [pdf/decrypted] $f"
    else
      emit_marker "$f" "ENCRYPTED" "user-password-protected; could not open with empty password. Needs password OR an unencrypted duplicate."
    fi
    return
  fi
  pdftotext -layout "$f" "$txt" 2>/dev/null
  cnt=$(wc -c < "$txt" 2>/dev/null | tr -d ' '); cnt=${cnt:-0}
  if [ "$cnt" -lt "$OCR_THRESHOLD" ]; then
    if have pdftoppm && have tesseract; then
      local tmp; tmp="$(mktemp -d)"
      pdftoppm -r "$DPI" -png "$f" "$tmp/pg" >/dev/null 2>&1
      { provenance "$f" "pdftoppm ${DPI}dpi + tesseract OCR"; } > "$txt"
      local n=0
      for img in "$tmp"/pg*.png; do
        [ -e "$img" ] || break
        n=$((n+1)); echo "===== PAGE $n =====" >> "$txt"
        tesseract "$img" stdout >> "$txt" 2>/dev/null
      done
      rm -rf "$tmp"
      echo "  -> [pdf/OCR ${n}pp] $f"
    else
      emit_marker "$f" "TOOL-MISSING" "scanned PDF (<$OCR_THRESHOLD chars) needs pdftoppm+tesseract; not installed."
    fi
  else
    { provenance "$f" "pdftotext -layout"; cat "$txt"; } > "$txt.tmp" && mv "$txt.tmp" "$txt"
    echo "  -> [pdf/text] $f"
  fi
}

convert_one() { # path
  local f="$1" ext lc base txt
  ext="${f##*.}"; lc="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  base="$(slug "$f")"; txt="$OUT/$base.txt"
  case "$lc" in
    pdf) convert_pdf "$f";;
    png|jpg|jpeg|tif|tiff)
      if have tesseract; then { provenance "$f" "tesseract OCR"; tesseract "$f" stdout 2>/dev/null; } > "$txt"; echo "  -> [image/OCR] $f";
      else emit_marker "$f" "TOOL-MISSING" "image OCR needs tesseract."; fi;;
    rtf|doc|docx)
      if have textutil; then { provenance "$f" "textutil"; textutil -convert txt "$f" -stdout 2>/dev/null; } > "$txt"; echo "  -> [doc] $f";
      else emit_marker "$f" "TOOL-MISSING" "needs macOS textutil."; fi;;
    xlsx)
      if have python3; then { provenance "$f" "python3 xlsx->tsv"; } > "$txt"; xlsx_to_tsv "$f" "$txt.body" && cat "$txt.body" >> "$txt" && rm -f "$txt.body"; echo "  -> [xlsx] $f";
      else emit_marker "$f" "TOOL-MISSING" "xlsx needs python3."; fi;;
    csv|tsv|txt|md)
      { provenance "$f" "copy"; cat "$f"; } > "$txt"; echo "  -> [text/copy] $f";;
    pages|numbers|key)
      # iWork bundles often embed a PDF preview at <bundle>/QuickLook/Preview.pdf
      if unzip -l "$f" 2>/dev/null | grep -qi 'QuickLook/Preview.pdf'; then
        local tmp; tmp="$(mktemp -d)"; unzip -o -j "$f" '*Preview.pdf' -d "$tmp" >/dev/null 2>&1
        local pv; pv="$(ls "$tmp"/*.pdf 2>/dev/null | head -1)"
        if [ -n "$pv" ]; then convert_pdf "$pv"; mv "$OUT/$(slug "$pv").txt" "$txt" 2>/dev/null; echo "  -> [iwork/preview-pdf] $f"; rm -rf "$tmp"; return; fi
        rm -rf "$tmp"
      fi
      emit_marker "$f" "ESCALATE" "Apple iWork file with no extractable PDF preview; needs Pages/Numbers/Keynote export.";;
    zip)
      { echo "# ZIP manifest (contents not auto-expanded):"; unzip -l "$f" 2>/dev/null; } > "$OUT/$base.manifest.txt"; echo "  -> [zip/manifest] $f";;
    *) emit_marker "$f" "ESCALATE" "unhandled file type .$lc";;
  esac
}

echo "convert-source: src=$SRC out=$OUT ocr-threshold=$OCR_THRESHOLD dpi=$DPI"
for t in pdftotext pdfinfo pdftoppm tesseract textutil qpdf python3; do
  have "$t" && echo "  tool OK: $t" || echo "  tool MISSING: $t"
done
echo "---"
if [ -d "$SRC" ]; then
  ( cd "$SRC" && find . -type f ! -name '.DS_Store' -print0 ) | while IFS= read -r -d '' rel; do
    convert_one "$SRC/${rel#./}"
  done
else
  convert_one "$SRC"
fi
echo "--- done. Outputs + markers in $OUT"
