# faed_provenance (cycle 37) — saved by main loop (agent could not write the file)
Scoring: unigram log-likelihood under best digit->letter map (saturated -1233.02), parametric pG from 400 sims; stationarity
checks (change point 33.3, w30 dispersion 193.3, longest pair-avoiding run, lag-1 MI) from 300 sims each.
Rejected: uniform base-9 (G=37.8), all ASCII-decimal-code variants (G=117-446), hex / K!=10 symbol families, Phase 3.2 board on
plain English (G=79.6), merged digit in any letter but g (next best i G=55).
Viable on counts (within ~4 nats): uniform decimal with 0 merged into g; 9-column board escapes g,i (+number block); P32 board + number block.
Stationarity: every stationary model (uniform digits, any transposed checkerboard) fails (p 0.003-0.04); untransposed
checkerboards add lag-1 dependence faed lacks. Only survivor: piecewise source — >=~70% raw decimal digits (g = two digits) plus a
minority segment of different makeup, untransposed (P32+70% number block: pG 0.20, p_cp 0.95, p_w30 0.49, p_lag1 0.80). Weak
(AIC favours split, BIC does not).
Implied decode (bulk = decimal digits with g ambiguous) already exhausted as TEXT by main loop (zero_dfs, subst_sweep, faed540).
Suggested (not run, blind-ish): 76-78-digit windows as decimal private keys vs prize address (~3k readings).
Files: models.py, runA/B.log, models_A/B.json, period_kfam.py/.log, decode_fit.py.
