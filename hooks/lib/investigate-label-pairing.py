"""offering.md label-pairing scanner. Reads content from stdin, tokens-file
from argv[1]. Exits 1 with violation message on stdout if a diagnosis label
appears in a paragraph without a process-description marker."""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from investigate_canon import match_copy
except Exception:
    def match_copy(s):
        return s

text = match_copy(sys.stdin.read())
tokens_path = sys.argv[1]

tokens = []
with open(tokens_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-') or line.startswith('|'):
            continue
        tokens.append(line)
tokens = [t for t in tokens if len(t) >= 3]

pairing_markers = [
    'meaning', 'pathway', 'process', 'mediator', 'mediators', 'release',
    'byproduct', 'downstream', 'upstream', 'mechanism', 'mechanisms',
    'producing', 'produced by', 'caused by', 'driven by', 'mediated by',
    'i.e.', 'that is,', 'discriminator',
]

# Strip fenced code blocks
text2 = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
# F5: strip inline code spans and exempt the trailing '## Labels referenced' section,
# matching investigate-diagnosis-attribution.py so a conformant labels section (where the
# tokens legitimately live, unpaired) does not false-trip the pairing check.
text2 = re.sub(r'`[^`]*`', '', text2)
text2 = re.split(r'(?im)^##\s+labels referenced.*?$', text2)[0]

# Split into paragraphs (blank-line separated)
paragraphs = re.split(r'\n\s*\n', text2)

for para in paragraphs:
    pl = para.lower()
    found = []
    for tok in tokens:
        if re.search(r'(?i)\b' + re.escape(tok) + r'\b', para):
            found.append(tok)
    if not found:
        continue
    if any(m in pl for m in pairing_markers):
        continue
    print(f'OFFERING_LABEL_UNPAIRED: labels {found} in paragraph without process description: {para.strip()[:300]}')
    sys.exit(1)

sys.exit(0)
