# Round 8 Fix Verification — Instructions for the Reviewer

**Read this document in full before opening any other file.**

You audited this engine on 4 October 2026, in round 8 of its independent audits. This
request asks whether the defects found since then were fixed, and whether fixing them
broke anything. It is a single request: you keep nothing between calls, so everything
you need is in this message.

This document was written by Claude, the AI model that wrote most of the fixes you are
asked to check, under a delegation from the project's owner, Viktor. He decides what
your report leads to. The weaknesses that brings are listed in Section 7.

---

## 1. What is in this message

After this document come these files, each between a BEGIN FILE and an END FILE marker
carrying its name. Their bytes are unmodified.

- **Your own round-8 report**, run 2, verbatim:
  `docs/audit_reports/round8_mimo-v2.6-pro_run2_2026-10-04/turn1_report.md` (your Parts
  1–6) and `…/turn2_report.md` (your Part 7 reply). Your findings are F1–F10 there.
- **The rulings** that decided what was fixed and how: an excerpt of
  `docs/PHASE7_DECISIONS.md`, unbroken, from "Ruling, 5 October 2026 — round 8 triaged"
  to the end of "Decision, 16 October 2026 — round 8's fix verification". It includes
  one entry that is not a ruling ("Position, 6 October 2026 … not ruled"); it is there
  only so the excerpt has no gap. The rulings are the fixer's account of what each change
  does, not evidence that it does it.
- **The Constitution**, the same audit copy you read in round 8.
- **`engine.diff`**: every change to the engine's source since the code you read. Your
  round-8 package was built from `e186423` (tagged `round7-sent-2026-09-30`) and sent
  from `217ede6` (tagged `round8-sent-2026-10-04`); the engine's source is the same at
  both, which the script that sends this message checks. The diff runs from `e186423` to
  the commit this message was built from.
- **The engine's source in full**, at that commit: every `.py` file the engine's own code
  fingerprint covers, each as its own file.
- **`tests_changed.diff`**: the changes, over the same span, to the test files that
  existed at `e186423`.
- **The test files added since `e186423`**, in full. The script that sends this message
  has a test file of its own, which is left out: it tests the sending, not the engine.

Commit hashes below name commits; the package carries no per-commit history, only the two
diffs from `e186423`.

## 2. What you are asked — five questions, in this order

### A. The stop: the release gate's question

The project's owner ruled on 5 October that the stop must not depend on directional
conviction or on trend health, as a break of Item 14 ("Directional conviction must never
be treated as equivalent to risk"), rated Critical because it reached live decisions
(the rulings, "Ruling, 5 October 2026 — round 8 triaged", point 1). That ruling came
from a review Claude wrote, not from your report. Your report read the same formula —
your F1 quotes `trend_factor * bias_factor` in it — rated what you found there Major
under Item 6, and returned no Critical.

The fix landed at `c2b07fb`: the stop multiplier is now
`stop_mult = ATR_STOP_MULT * vol_multiplier` (`models/risk_model.py`, line 400).

Answer two things:

1. **Does the fix hold?** Anywhere the stop, its distance or its multiplier is computed,
   recorded, printed or checked, does anything still depend on the bias score, on
   conviction, or on trend health? Verdict: **Holds / Does not hold / Partly holds**,
   citing the code.
2. **Does any change since your package add a Critical?** **Yes / No.** For each yes,
   the location and the clause it breaks, under the Constitution's own rubric ("how a
   finding gets recorded").

You are not asked to re-rate the ruling. If you disagree with it, say so in Section E;
it does not change your answer here.

### B. Your own findings that were fixed

For each, check the code against **your own words** in your report, and give a verdict:
**Fixed / Not fixed / Partly fixed / Not verifiable**, with one or two lines citing the
code that supports it. "Not verifiable" must say what is missing.

- **F1** — by the fix in A: the lineage comment and the decision contract's docstring
  were corrected (`c2b07fb`).
- **F2** — `classify_risk_regime` reads only the volatility state and the stop distance
  (`models/risk_model.py`, lines 498–547; `fcb7823`).
- **F3** — a frame with no readable time axis is rejected (`data/validation.py`, line
  352; `ae37795`).
- **F5** — the line reads "from the band's midpoint" (`core/panel_render.py`, line 644;
  `9d00d99`).
- **F6** — `clean_series` refuses `interpolate` (`indicators/indicators.py`, lines
  104–124; `27d3ed5`).
- **F8** — one VWMA name, and the MOMENTUM line is gone (`core/panel_render.py`, lines
  929–935; `9051ffd`).
- **F9** — each of its four claims separately (`e5ac20a`).
- **Your Part 4's three test shapes** (`f00bef6`): the golden coverage test that
  returned instead of skipping; the test that checked only that a string is in a source
  file — and, beside it, the SuperTrend level test you named with it; and the watched
  error count written as 29 where the suite runs at 32. Each separately.

### C. Every other change to code you read

The fixes changed code you read in round 8 for reasons other than your findings, and each
such change can carry a new defect. Check each against the ruling that defines it (named
in brackets) for new defects — not as a fix of yours:

- fix 2, no trade under ADX 20 (`1b25f36`; the triage, point 4);
- B6, runs on pinned data keep records of their own (`9e507b1`; point 6);
- N5, Bitcoin reference only (`6469a67`; point 7);
- the fallback sweep (`797bdc9`) and the two repeated readings (`69c92d6`) ("Ruling,
  13 October 2026 — the fallback sweep …");
- B4's labels (`22a9a35`; "Ruling, 14 October 2026");
- B7 (`d77a8c4`), B9 (`64ad625`) and B10 (`9ea1cf3`) (the three rulings of 15 October
  that name them).

For each: **No new defect found**, or each defect with its location, the clause it
breaks and its severity. And for each ruling: **name any claim it makes about the code
that the code does not support.** That is the class of defect your F9 found, and the
rulings are where this project is most likely to have repeated it.

### D. Declared not fixed

These were not fixed, by decision. Do not report them as failed fixes. Say only if a
change since your package made one of them worse.

- **F4** — `macro_multiplier` still stands (`models/entry_model.py`, lines 387–389).
- **F7** — the spike window is still `min(config.VWMA_LENGTH, len(vol))`
  (`indicators/indicators.py`, line 808).
- **F10** — the gate still stands (`models/decision_model.py`, line 678).
- **Your Part 4's other named tests** — the absence scans of your shape 1, and your
  shape 4.
- **Your Part 7 reply's §1(3)** — the default responses' `0.0` still stands
  (`models/entry_model.py`, line 120; `indicators/trend_health.py`, line 22).
- **Your Part 7 reply's §1(5)** — not checked by the project.

### E. Anything else

Only if you have it: anything else you noticed, unprompted, including disagreement with
a ruling. It does not change your answers to A–D.

## 3. How to answer

Use these headings, in this order, so a skipped item shows: **A. The stop**, **B. Your
findings**, **C. Other changes**, **D. Declared not fixed**, **E. Anything else**,
**F. About this reading**. Under B and C, one sub-heading per item, in the order listed
above, each opening with its verdict.

Cite code by file and line, and quote it. Line numbers in this document are those of the
commit this message was built from. Where you cannot check something from what is here,
say "Not verifiable" and what is missing: a guess written as a verdict is worse than no
verdict.

## 4. About this reading (your Section F)

1. **Which model are you?** Say what you know. "I do not know" is an acceptable answer.
   This project's record says both of your round-8 runs named their author as Claude,
   while the provider's record named Xiaomi's endpoint.
2. **Recognition.** This repository is public. A model released after its first public
   commits may hold earlier versions of this code in its weights, and nobody can check
   that. If at any point you find yourself recognising code rather than reading it,
   say where.
3. **What you read closely, and what you did not.** This message is several times larger
   than a typical fix verification. Say which files you read in full and which you
   searched.

## 5. What this request is not

It is not scored on planted test bugs, and none are planted. It is not a fresh audit:
you are not asked to grade the forty-four rules again. It is one run; the project may
send at most one more, decided only after reading this one.

## 6. What your report decides

The project's release gate has been closed since 5 October. It reopens only on a report
that says the fix in A holds and that no change since your package adds a Critical, and
only once Viktor has accepted that report. A report that finds the fix incomplete, or a
new Critical, keeps the gate closed and goes to his triage. Your other answers go to
triage either way.

## 7. What this arrangement weakens

Stated so you can weigh it, not so you defer to it:

- The fixer chose what you are asked, wrote this document and will read your reply.
- The Critical you are asked about was ruled from the fixer's own review; you rated what
  you found in the same formula Major. Your "holds" confirms the fix of a defect you did
  not raise as Critical.
- The rulings in this package are the fixer's account of each change. They frame your
  reading even though you are asked to check them.
- Your two round-8 runs found different things. A single verdict is one sample of how you
  read this code.
