F1: **Fixed** — all four scoped locations now named: `models/entry_model.py: CONFLUENCE_BOOST_MULT=1.05 / CONFLUENCE_PENALTY_MULT=0.90` replaces six bare `1.05/0.90`; `indicators/indicators.py: SPIKE_RATIO=10.0` at module scope; `models/btc_context.py: CORRELATION_WINDOW=30` + `core/engine_core.py: compute_correlation_beta(df_struct["close"], df_btc_struct["close"])` with no `window=30` literal; `structure/structure.py: REGIME_HYSTERESIS_THRESHOLD=0.0015` + `threshold = self.REGIME_HYSTERESIS_THRESHOLD`.

F2: **Fixed** — `core/engine_core.py risk={...}` no longer contains `confidence_score` — comment: “drop rather than rename” — leaving `models/signal_router.py: "confidence_score": float(confidence)` as sole meaning.

F3: **Fixed** — `models/signal_router.py _build_decision_object` all six now NaN-passthrough: `zone_lower/zone_upper/distance_from_zone/atr_stop/current_price` via `self._finite_or_nan(...)` and `targets = risk.get("targets", (nan,nan,nan))` with malformed fallback to `(nan,nan,nan)`.

F4: **Fixed** — `core/panel_render.py: targets/current_price/stop_loss` now `safe_float(..., float("nan"))` with `t1=t2=t3=nan` fallback and `math.isfinite()` guards printing `not located/not computed/not available` instead of `$0.0000`.

F5: **Fixed** — `models/decision_model.py: AGGRESSIVE_TREND_HEALTH_MIN=75.0 / AGGRESSIVE_ENTRY_SCORE_MIN=70.0 / CONSERVATIVE_TREND_HEALTH_MIN=50.0` replaces bare `>=75/>=70/>=50`, and `MIN_ACTION_BIAS=30.0` vs `RAW_BIAS_THRESHOLD=20.0` documented as intentional two-thresholds both already named/fingerprinted.

Bonus, unprompted: `models/signal_router.py` has duplicate `@staticmethod` stacked above `_finite_or_nan` — harmless, cleanup only.
