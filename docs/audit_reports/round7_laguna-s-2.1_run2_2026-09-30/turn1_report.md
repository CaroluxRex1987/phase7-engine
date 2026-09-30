**Model identity:** I am Poolside's **Meta-Muse Spark 1.3**, a model from a lab that has had no prior exposure to this project.

---

**Part 1 — Verdict table**

| Item | Rule | Verdict |
|---|---|---|
| 1 | Tool, Not Autonomous Actor | Compliant |
| 2 | No Future Information / Look-Ahead Bias | Compliant |
| 3 | Data Integrity | Compliant |
| 4 | Determinism | Compliant |
| 5 | Reproducibility | Compliant |
| 6 | Traceability | Compliant |
| 7 | No Unsupported Predictive Claims | Compliant |
| 8 | Epistemic Honesty | Compliant |
| 9 | Every Measurement Has a Precise Definition | Compliant |
| 10 | Consistent Semantics | Compliant |
| 11 | No Circular Reasoning | Partially compliant |
| 12 | No Hidden Decision-Affecting State | Compliant |
| 13 | Fail Safely | Compliant |
| 14 | Risk Is Not Conviction | Compliant |
| 15 | Empirical Evidence Supersedes Theoretical Expectation | Compliant |
| 16 | Complexity Must Provide Demonstrated Value | Compliant |
| 17 | Backtesting Must Be Isolated From the Core Engine | Compliant |
| 18 | Read-Only Market Access | Compliant |
| 19 | Withdrawal Permissions Are Never Enabled | Compliant |
| 20 | Credentials Are Never Exposed | Compliant |
| 21 | Operator Credentials Stay With the Operator | Compliant |
| T2-1 | Separation of responsibilities | Compliant |
| T2-2 | Observation → interpretation → decision → risk/action | Compliant |
| T2-3 | Explicit interfaces/contracts | Compliant |
| T2-4 | Explicit configuration | Compliant |
| T2-5 | Modular design | Compliant |
| T2-6 | Controlled dependencies | Compliant |
| T2-7 | Explicit, evaluated changes to interfaces or behavior | Compliant |
| T3-1 | Hypothesis-driven development | Not verifiable |
| T3-2 | Controlled changes | Compliant |
| T3-3 | Automated tests | Compliant |
| T3-4 | Regression tests | Compliant |
| T3-5 | Fixed evaluation datasets | Compliant |
| T3-6 | Version control | Compliant |
| T3-7 | Known-good checkpoints | Compliant |
| T3-8 | Reproducible experiments | Compliant |
| T3-9 | Rollback capability | Compliant |
| T3-10 | Documentation of significant decisions | Compliant |
| T4-1 | Robustness over optimization | Compliant |
| T4-2 | Generalization over historical fit | Compliant |
| T4-3 | Explainability over unnecessary opacity | Compliant |
| T4-4 | Stability over flashy outputs | Compliant |
| T4-5 | Useful information over more information | Compliant |
| T4-6 | When multiple designs already satisfy every invariant equally well, prefer the simpler one | Compliant |

---

**Part 2 — Findings (Non-compliant / Partially compliant, ordered by severity)**

1. **Item 11 — No Circular Reasoning**  
   - **Location:** `models/bias_engine.py` — the `calculate_dynamic_bias` function, specifically the comments around the dependency graph.  
   - **What the code does:** The code combines six factors into `bias_score`, four of which are derived from the same input: the recent direction of `close` (EMA slope, short-vs-long mean gap, ATR-banded flip, and price vs. its 50-EMA). These four factors enter the blend with the same sign and move in the same direction, creating a risk of the same underlying signal reinforcing itself through multiple paths.  
   - **Which clause it breaks:** "A signal must not be allowed to reinforce itself through multiple derived layers and then be presented as independent confirmation."  
   - **What goes wrong in practice:** A sustained trend in a single direction causes all four derived factors to agree by construction, which can amplify the perceived strength of a signal that is, in effect, the same underlying observation counted four times. While each factor uses a different window or arithmetic, their shared input means their agreement is not independent confirmation. The code acknowledges this risk in its comments and leaves the weights unchanged, stating it is a trading judgment to be resolved later.  
   - **Severity:** Major — The risk is that a single market direction is presented as four independent confirmations in the reasoning text (e.g., "structure agrees with the direction", "macro agrees"), misleading the operator into believing the confidence score reflects multi-factor validation when it largely reflects one. It does not produce wrong numbers, but it undermines the epistemic honesty of the explanation. The impact is mitigated by the fact that the code documents this explicitly and that the bias_label and decision logic correctly treat the score as a single measurement.

---

**Part 3 — Not verifiable**

- **Item T3-1 (Hypothesis-driven development):** The Constitution requires that changes be made following a hypothesis-testing cycle. The version-control history shows a large number of commits, many with descriptive messages, but it does not provide evidence of documented hypotheses, experiments, or measurements at each step. Without access to prior planning documents or Engineering Notes content (which is referenced but not provided in the package), I cannot confirm that changes were always hypothesis-driven. The process artifact is present, but the substance of the hypothesis behind each change is not visible.

---

**Part 4 — Test suite assessment**

**Section 7.3 results:** I found **zero** instances of tests that pass without proving anything. Specifically:
- No test iterates a collection and asserts nothing on an empty result.
- No test injects a failure at a point the code path never reaches without it being verified.
- No test asserts only absence in a way that would pass if the feature vanished.
- No test's setup contradicts what it claims to test.
- No test returns instead of skipping on an unmet precondition.
- No test's fixture can no longer produce the condition it was written for.

The suite is exceptionally strong. It is heavily focused on asserting the absence of a defect (e.g., checking that a fabrication never occurs, that a default default never fires), which makes many tests precise regression guards. The tests for look-ahead bias (`test_no_lookahead.py`), fabricated defaults (`test_router_no_fabricated_zero_defaults.py`), and data integrity (`test_data_integrity.py`) are particularly rigorous. The suite also includes strong negative controls and tests that verify the code path itself, not just the result (e.g., `test_run_tests_filter_matching.py` checks that a filter matching nothing fails loudly).

**Overall judgement:** This suite tests the engine, not just that it hasn't changed. It is highly adversarial towards its own code, with numerous tests designed to fail if a defect silently returns.

---

**Part 5 — Release gate**

The Constitution's gate condition is that no Critical Tier 1 finding stands unresolved.

- **Verdict:** **Met.**
- **Reasoning:** The only Non-compliant or Partially compliant finding I identified (Item 11) is classified as Major, not Critical. It presents a risk of misleading the operator about the independence of confirmation signals but does not produce a wrong or fabricated number (Critical is reserved for defects that "produce a wrong or fabricated number the operator would reasonably act on, or an assertion by the engine that something happened when it did not"). All four Tier 1 Critical items (Items 3, 6, 18, and the credential items 19-21) are Compliant. Therefore, the release gate is satisfied on my findings alone.

---

**Part 6 — Observations outside the Constitution**

1. **Claimed fixes I could not confirm:**  
   - The comment in `models/decision_model.py` regarding Item 14 mentions a past ruling where `trend_health` was removed from `classify_risk_regime`. The code reflects this (the third parameter was renamed from `trend_health` to `adx`). However, I could not access `docs/PHASE7_DECISIONS.md` to confirm the ruling's exact wording. The code change itself is consistent with the comment.  
   - The `test_no_lookahead.py` test states that `clean_series` "used to end with `fillna(median_val)`", which is presented as a past fabrication. The current code does not contain this pattern, so the claim holds, but I cannot verify the historical state.

2. **Places where I relied on a comment rather than the code:**  
   - When reading the long explanatory comments in `core/engine_core.py` and `core/decision_log.py`, I found myself occasionally trusting phrases like "AUDIT FINDING" or "Finding 3" to summarize a past defect. In each case, I traced back to the actual code to verify the current state (e.g., confirming `engine_core.py` no longer passes `structural_level` to `calculate_stop_targets`, verifying the `code_fingerprint.py` logic by its tests). I did not let a comment stand unchallenged for an actual verdict.

3. **The `btc_context` block's `degraded_inputs`:**  
   - The code in `core/engine_core.py` carefully separates BTC-side indicator failures into `btc_context["degraded_inputs"]` and explicitly avoids appending them to the top-level `degradation` list. The test `test_btc_degradation_stays_informational.py` rigorously enforces this. This is a well-designed isolation boundary that prevents an optional informational feature from accidentally blocking trades.

4. **The `_state_path` and `_save_state` atomic write:**  
   - The engine's C3 state persistence uses a temp-file-and-replace pattern. This is a robust solution to a critical class of bug (partial writes corrupting state). The test `test_engine_state_atomic_write.py` effectively reproduces the crash scenario and verifies the prior state is preserved.

5. **The `run_tests.py` filter guard:**  
   - The test `test_run_tests_filter_matching.py` checks that a filter matching nothing exits non-zero. This is a subtle but important guard against CI misconfiguration, and it is implemented as a behavioral test with subprocesses, which is appropriate for checking exit codes.