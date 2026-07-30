# Failure modes this case tests

**Primary:** memory-based base-rate inflation. The orchestrator has historically
quoted NC-CAH prevalence as "1 in 50 Ashkenazi" from memory when the actual
published lift is ~1.2-2.4× background for Ashkenazi-specific symptomatic
heterozygotes (Carmina 2017; Dewailly 2017; New 2006). The case enforces:

1. NC-CAH is enumerated as a route alongside PCOS in Step 3 (not silently
   dropped, not silently promoted).
2. The candidate ledger entry for NC-CAH has both a `verification:` field and
   an `impact:` field populated.
3. The numerical lift cited has a paper citation (Carmina/Dewailly/New
   /Speiser) — not a remembered round-number ratio.
4. The discriminator named is 17-OHP measurement (the cheap-and-specific
   test) — not a generic "endocrinology referral."
5. NC-CAH starts at T3 (mechanistically plausible) — not jumped to T2.
6. None of the banned-escalation words appear in the synthesis.

Linked SKILL.md rule: register §"Every fact gets verified, then weighted"
(both Check 1 and Check 2); Step 3 (Routes) Pass B.
