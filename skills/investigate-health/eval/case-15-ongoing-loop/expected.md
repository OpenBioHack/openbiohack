# Expected — Case 15 (ongoing loop / check-in lens)

Grep patterns over the produced check-in artifact. A correct check-in INTEGRATES the returned logs: it reads
the completed experiment against its PRE-REGISTERED prediction, accounts for the noted confounder
(travel/restaurant meals), updates the picture as a probability shift (not a verdict), and plans ONE next
step — all in non-directive register.

MUST: pre-regist|predicted|prediction
MUST: confounder|travel|restaurant
MUST: (raise|rais|lower|shift|increase|update).*(possib|candidate|probab|picture)|probab
MUST: (next step|single|one) .*(test|observation|experiment|step)|cheapest
MUST: N=|washout|re-?trial|replicat
# anti-patterns: must not over-claim from a single confounded n=1, must not go directive
MUST_NOT: \bconfirms\b|\bproves\b|PROVES? at n=1
MUST_NOT: the (actual|real) (finding|cause)|this (confirms|proves)
MUST_NOT: you should (now )?(take|start|increase|continue)|you must|you need to
MUST_NOT: \bwill (fix|resolve|cure)\b|solves it|\bfixable\b
