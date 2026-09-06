# Section 11 confirmation run — Kimi round-4, Finding 1

Kimi's round-4 report asked for exactly one run. This directory is that run, made on
**6 September 2026 against unmodified code, before any fix**, so the defect is observed
rather than argued.

## What is here

| file | what it is |
|---|---|
| `section11_confirm.py` | the harness. Run it from anywhere: `python docs/audit_reports/round4_kimi-k3_2026-09-05/section11_confirmation/section11_confirm.py` |
| `run_A_control.txt` | fixtures exactly as committed — the negative control. Completes. |
| `run_B_shift.txt` | BTC timestamps shifted +2h, zero shared timestamps. **The case.** |
| `run_C_flat.txt` | BTC's last 60 candles flat — the optional zero-variance variant. Secondary: a flat series also moves BTC-side ATR and volatility. |
| `isolated_phase7_decision_log_aerousdt.jsonl` | the decision log the three runs produced, in their redirected log directory |
| `isolated_phase7_state_AEROUSDT_4h.json` | the state file they produced, likewise |

## The result

B and C both return

    Decision object construction failed: float() argument must be a string or a real
    number, not 'NoneType'

which is the distinguishing output Kimi named. A completes on the same harness with a
measured correlation, which is what makes B's failure mean something.

## Two isolations, both deliberate

1. **Network.** `requests.get`, `.post` and `Session.request` are replaced with functions
   that raise, so a run that reaches the API says so instead of quietly succeeding against
   live data.
2. **The record.** `config.LOG_DIR` is repointed at a temporary directory. The first version
   of this harness did not do that and appended three records to the real
   `logs/phase7_decision_log_aerousdt.jsonl` while overwriting
   `logs/phase7_state_AEROUSDT_4h.json` — a diagnostic writing into the record the audit is
   about. A harness that cannot reach the real log cannot contaminate it.

## The thing the run found that the report does not contain

Read `isolated_phase7_decision_log_aerousdt.jsonl`. Record 1 (healthy) carries `lineage` and
`provenance` with `input_hashes`, `run_hash` and the pinned flag. Records 2 and 3 carry
`error`, `symbol`, `timeframe` and `decision_log_path`, and nothing else. The broad `except`
discards the lineage along with the analysis, so the log stores a record Item 6 cannot trace
to any input.

Full narrative in `docs/PHASE7_NEXT.md`, section "The Section 11 confirmation run".
