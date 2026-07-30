# Expected — Case 01

Grep patterns. Lines starting with `MUST:` are extended regex patterns that
must match somewhere in the produced artifact tree. `MUST_NOT:` patterns
must not match.

MUST: NC-CAH|non-classical CAH|21-hydroxylase deficiency
MUST: 17-OHP|17-hydroxyprogesterone
MUST: Ashkenazi
MUST: verification:
MUST: impact:
MUST: Carmina|Dewailly|New 2006|Speiser
MUST: \b(1\.[2-9]|2\.[0-4])x|lift.*1\.[2-9]|lift.*2\.[0-4]
MUST: T3|tier.*3|Tier 3
MUST_NOT: 1:50|1 in 50|1:100|1 in 100
MUST_NOT: confirms|proves|the reason is|this means
