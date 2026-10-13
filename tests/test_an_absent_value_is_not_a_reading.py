"""
The fallback sweep -- 13 October 2026.

WHAT WAS WRONG

The panel and the router read most of the decision with dict.get(key,
default), and many of the defaults were readings: BIAS NEUTRAL, VOLATILITY LOW,
RISK REGIME NORMAL RISK, STATUS ACTIVE ENTRY ZONE, ACTION WAIT, an entry score
of 0.0, a reward multiple of 2.0, no exhaustion, no divergence, no stress,
nothing degraded. None of them could fire on the engine's path -- the router
writes every key the panel reads, and the engine writes every key the router
reads -- which is how they survived. The shape is the one this project keeps
finding after audits: a constant on a path a healthy run never takes, waiting
for one change elsewhere to make it the live path.

Found in pieces: the TREND line by F9 (12 October), eleven more panel lines
building it, three more filing that ruling, and the rest by an inventory of
every default in the two files (DECISIONS, "Ruling, 13 October 2026 -- the
fallback sweep").

THE SHAPE, AS RULED

- A value that is only printed or recorded falls back to the router's own
  value for an absent one: UNKNOWN (UNKNOWN STRUCTURE, UNKNOWN VOLUME, UNKNOWN
  RISK) for a label, NaN for a number, NOT MEASURED for the correlation label.
- A value with no UNKNOWN in its type (a bool, a list, a section of the
  engine's output) and a value the engine computes with are read directly: a
  missing key is a defect, and fails as one.
- Kept: defaults that were already honest -- UNKNOWN, NaN, None, "" for
  nothing written, a sentence saying nothing was produced, and the producer's
  own not-measured spellings.

WHAT THESE TESTS HOLD

1. The inventory. Every default in core/panel_render.py and
   models/signal_router.py is listed below with the reason it is allowed. A
   default added anywhere in either file fails the test until somebody lists
   it and says why -- the next NEUTRAL cannot arrive unnoticed. A listed
   default that is gone fails it too, so the list cannot rot into a list of
   things that used to be true.
2. The panel, rendered from a decision with every reading absent, prints
   UNKNOWN on each line that used to print a reading -- and, the negative
   control, prints the readings when they are present.
3. The router refuses an absent boolean rather than inventing False, and the
   refusal keeps the run's provenance and lineage; a complete input still
   builds. An incomplete BTC block becomes "unavailable" rather than an error
   for the asset's whole analysis (Bitcoin is reference only).
4. engine_core reads the six values the bias and entry computations use
   directly, not with a default.

Source-text tests where a behavioural test cannot see the defect: a default on
a path nothing reaches is invisible to any run. Fixture-free, per
run_tests.py; nothing here needs pandas_ta.
"""

import ast
import collections
import math
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

PANEL = "core/panel_render.py"
ROUTER = "models/signal_router.py"
ENGINE = "core/engine_core.py"


# ======================================================================
# 1. The inventory
# ======================================================================

def _read(relpath):
    with open(os.path.join(REPO, relpath), encoding="utf-8") as fh:
        return fh.read()


def _defaults(src):
    """
    Every default in the file, as (function, receiver, key, default) source
    text, normalised by ast.unparse so quoting and line breaks do not matter:

    - x.get(key, default), unless the default is itself a .get() call (that
      inner call is listed on its own);
    - a or <constant>;
    - <something reading .get()> if ... else <string constant>.
    """
    tree = ast.parse(src)
    found = collections.Counter()

    def visit(node, stack):
        for child in ast.iter_child_nodes(node):
            names = stack
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names = stack + [child.name]
            where = ".".join(names) or "<module>"
            if (isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute)
                    and child.func.attr == "get" and len(child.args) == 2):
                default = child.args[1]
                inner_get = (isinstance(default, ast.Call)
                             and isinstance(default.func, ast.Attribute)
                             and default.func.attr == "get")
                if not inner_get:
                    found[(where, ast.unparse(child.func.value),
                           ast.unparse(child.args[0]), ast.unparse(default))] += 1
            if (isinstance(child, ast.BoolOp) and isinstance(child.op, ast.Or)
                    and isinstance(child.values[-1], ast.Constant)):
                found[(where, ast.unparse(child.values[0]), "<or>",
                       ast.unparse(child.values[-1]))] += 1
            if (isinstance(child, ast.IfExp) and isinstance(child.orelse, ast.Constant)
                    and isinstance(child.orelse.value, str)
                    and ".get(" in ast.unparse(child.test) + ast.unparse(child.body)):
                found[(where, ast.unparse(child.test), "<if-else>",
                       ast.unparse(child.orelse))] += 1
            visit(child, names)

    visit(tree, [])
    return found


UNKNOWN_LABEL = "an absent label reads UNKNOWN, the router's own word for it"
SECTION = ("a section guard: an absent or malformed section is read as empty, "
           "and every line then prints its own absent value")
HONEST = "already says nothing was produced"

# (function, receiver, key, default) -> (count, reason)
ALLOWED = {
    PANEL: {
        # metadata
        ("render_panel", "decision.get('symbol')", "<or>", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "decision", "'timeframe'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "decision", "'macro_bias'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        # section guards
        ("render_panel", "decision", "'bias'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'trend'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'structure'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'entry'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'risk'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'exit'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'explanation'", "{}"): (1, SECTION),
        ("render_panel", "decision", "'btc_context'", "{}"): (1, SECTION),
        # files
        ("render_panel", "decision.get('decision_log_path')", "<or>", "''"): (
            1, '"" means no log was written, and the panel then claims none'),
        ("render_panel", "decision.get('chart_path')", "<or>", "''"): (
            1, '"" means no chart was saved, and the panel then claims none'),
        ("render_panel", "risk.get('validation_note')", "<or>",
         "'No validation note was produced for this run.'"): (1, HONEST),
        # the decision and its reasons
        ("render_panel", "exit_data", "'action'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "explanation", "'reasons'", "[]"): (
            1, 'an empty list prints "No explanation available for this decision."'),
        ("render_panel", "bias", "'raw'", "'UNKNOWN'"): (2, UNKNOWN_LABEL),
        # BTC
        ("render_panel", "btc", "'available'", "False"): (
            1, "an absent flag means the block is unavailable, and the panel says so"),
        ("render_panel._correlation_lines", "btc", "'n_observations'", "0"): (
            1, "0 is compute_correlation_beta's own not-measured count; "
               "the panel prints NOT MEASURED for it"),
        ("render_panel._correlation_lines", "btc.get('n_observations', 0)", "<or>", "0"): (
            1, "the same not-measured count, for a None"),
        ("render_panel._correlation_lines", "btc", "'correlation_label'", "'NOT MEASURED'"): (
            1, "btc_context.NOT_MEASURED_LABEL"),
        ("render_panel", "btc", "'detailed'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "btc", "'regime'", "'UNKNOWN STRUCTURE'"): (1, UNKNOWN_LABEL),
        ("render_panel", "btc", "'volatility'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        # the reading lines
        ("render_panel", "structure", "'regime'", "'UNKNOWN STRUCTURE'"): (1, UNKNOWN_LABEL),
        ("render_panel", "bias", "'volatility'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "structure", "'sequence'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "trend", "'trend_direction'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "trend", "'momentum_mode'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "structure", "'volume_sentiment'", "'UNKNOWN VOLUME'"): (1, UNKNOWN_LABEL),
        ("render_panel", "risk", "'validation_state'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "risk", "'risk_regime'", "'UNKNOWN RISK'"): (1, UNKNOWN_LABEL),
        ("render_panel", "entry", "'entry_status'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("render_panel", "struct_candle.get('open_time')", "<if-else>", "''"): (
            1, "no candle time is printed when there is none"),
    },
    ROUTER: {
        ("SignalRouter.route_and_execute", "raw_output", "'macro_bias'", "'UNKNOWN'"): (
            1, UNKNOWN_LABEL + "; printed and recorded only"),
        ("SignalRouter.route_and_execute", "logged_to", "<or>", "''"): (
            1, '"" means the decision log was not written'),
        ("SignalRouter.route_and_execute", "decision", "'exit'", "{}"): (
            1, "a log line's guard"),
        ("SignalRouter.route_and_execute", "decision.get('exit', {})", "'action'", "'UNKNOWN'"): (
            1, "a log line; " + UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "risk", "'targets'",
         "(float('nan'), float('nan'), float('nan'))"): (
            1, "NaN is the router's value for an absent price (round 6, F3)"),
        ("SignalRouter._build_decision_object", "bias", "'raw'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "bias", "'detailed'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "bias", "'regime'", "'UNKNOWN STRUCTURE'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "bias", "'volatility'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "trend", "'momentum_mode'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "trend", "'divergence_direction'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "trend", "'trend_direction'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "structure", "'regime'", "'UNKNOWN STRUCTURE'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "structure", "'sequence'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "structure", "'volume_sentiment'", "'UNKNOWN VOLUME'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "entry", "'entry_status'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "risk", "'risk_reason'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "risk", "'risk_regime'", "'UNKNOWN RISK'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "risk", "'validation_state'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._build_decision_object", "risk", "'validation_note'",
         "'No validation note supplied.'"): (1, HONEST),
        ("SignalRouter._merge_btc_context", "btc_context", "'raw'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._merge_btc_context", "btc_context", "'detailed'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._merge_btc_context", "btc_context", "'regime'", "'UNKNOWN STRUCTURE'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._merge_btc_context", "btc_context", "'volatility'", "'UNKNOWN'"): (1, UNKNOWN_LABEL),
        ("SignalRouter._merge_btc_context", "btc_context", "'correlation_label'",
         "btc_context_module.NOT_MEASURED_LABEL"): (
            1, "btc_context.NOT_MEASURED_LABEL, the panel's own value for it"),
        ("SignalRouter._merge_btc_context", "btc_context", "'n_observations'", "0"): (
            1, "0 is compute_correlation_beta's own not-measured count"),
        ("SignalRouter._merge_btc_context", "btc_context.get('n_observations', 0)", "<or>", "0"): (
            1, "the same not-measured count, for a None"),
    },
}


def _check_inventory(relpath, src=None):
    found = _defaults(_read(relpath) if src is None else src)
    allowed = collections.Counter({k: v[0] for k, v in ALLOWED[relpath].items()})
    unlisted = found - allowed
    stale = allowed - found
    problems = []
    for key, n in sorted(unlisted.items()):
        problems.append(f"NOT LISTED ({n}x): {key}")
    for key, n in sorted(stale.items()):
        problems.append(f"LISTED BUT GONE ({n}x): {key}")
    return problems


def test_every_default_in_the_panel_is_listed_with_its_reason():
    problems = _check_inventory(PANEL)
    assert not problems, (
        "core/panel_render.py's defaults differ from the list in this file. "
        "A new one must be listed with the reason it is not a reading; one that "
        "is gone must come off the list:\n  " + "\n  ".join(problems))


def test_every_default_in_the_router_is_listed_with_its_reason():
    problems = _check_inventory(ROUTER)
    assert not problems, (
        "models/signal_router.py's defaults differ from the list in this file. "
        "A new one must be listed with the reason it is not a reading; one that "
        "is gone must come off the list:\n  " + "\n  ".join(problems))


def test_the_inventory_sees_a_reading_when_one_is_added():
    """The negative control for the two tests above: the same check, run on a
    copy of the panel's source with RISK REGIME's old reading put back."""
    src = _read(PANEL).replace("risk.get('risk_regime', 'UNKNOWN RISK')",
                               "risk.get('risk_regime', 'NORMAL RISK')", 1)
    assert src != _read(PANEL), "the control's edit did not apply"
    problems = _check_inventory(PANEL, src)
    assert problems == [
        "NOT LISTED (1x): ('render_panel', 'risk', \"'risk_regime'\", \"'NORMAL RISK'\")",
        "LISTED BUT GONE (1x): ('render_panel', 'risk', \"'risk_regime'\", \"'UNKNOWN RISK'\")",
    ], problems


# ======================================================================
# 2. The panel
# ======================================================================

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _render(decision):
    from core.panel_render import render_panel
    panel = render_panel(decision)
    assert isinstance(panel, str), "render_panel returned no panel"
    return ANSI.sub("", panel)


def _line(panel, prefix):
    for line in panel.splitlines():
        if line.strip().startswith(prefix):
            return line.strip()
    raise AssertionError(f"no line starting {prefix!r} in:\n{panel}")


def _absent_readings():
    return {"symbol": "TESTUSDT", "timeframe": "4h",
            "bias": {}, "trend": {}, "structure": {}, "entry": {}, "risk": {},
            "exit": {}, "btc_context": {"available": True}}


EXPECTED_WHEN_ABSENT = {
    "BIAS       :": "BIAS       : UNKNOWN",
    "STRUCTURE  :": "STRUCTURE  : UNKNOWN STRUCTURE",
    "SEQUENCE   :": "SEQUENCE   : UNKNOWN",
    "VOLUME     :": "VOLUME     : UNKNOWN VOLUME",
    "VALIDATION :": "VALIDATION : UNKNOWN (Score: not computed)",
    "VOLATILITY :": "VOLATILITY : UNKNOWN",
    "RISK REGIME:": "RISK REGIME: UNKNOWN RISK",
    "MACRO TREND:": "MACRO TREND: UNKNOWN",
    "STATUS        :": "STATUS        : UNKNOWN",
    "DECISION      :": "DECISION      : UNKNOWN",
    "BTC BIAS      :": "BTC BIAS      : UNKNOWN",
    "BTC REGIME    :": "BTC REGIME    : UNKNOWN STRUCTURE | Vol: UNKNOWN",
    "BROAD MARKET STRESS:": "BROAD MARKET STRESS: UNKNOWN",
}


def test_a_panel_with_every_reading_absent_prints_unknown_not_a_reading():
    panel = _render(_absent_readings())
    wrong = {}
    for prefix, expected in EXPECTED_WHEN_ABSENT.items():
        line = _line(panel, prefix)
        if line != expected:
            wrong[prefix] = line
    assert not wrong, f"lines that print something nobody measured: {wrong}"
    assert "Exit watch was not computed for this run." in panel
    assert "No exit-watch flags are active right now." not in panel


def test_negative_control_present_readings_still_print():
    decision = _absent_readings()
    decision.update({
        "macro_bias": "BULLISH",
        "bias": {"raw": "BULLISH", "detailed": "BULLISH CONFIRMED",
                 "regime": "BULLISH TREND", "volatility": "HIGH VOLATILITY"},
        "structure": {"regime": "BULLISH TREND", "sequence": "BULLISH SWING SEQUENCE (HH-HL)",
                      "volume_sentiment": "BULLISH VOLUME SUPPORT"},
        "risk": {"validation_state": "NEUTRAL", "risk_regime": "HIGH VOLATILITY RISK"},
        "entry": {"entry_status": "NEAR ZONE"},
        "exit": {"action": "WAIT"},
        "exit_watch": [],
        "btc_context": {"available": True, "detailed": "BEARISH", "regime": "BEARISH TREND",
                        "volatility": "LOW VOLATILITY", "broad_market_stress": False},
    })
    panel = _render(decision)
    assert _line(panel, "BIAS       :") == "BIAS       : BULLISH CONFIRMED"
    assert _line(panel, "STRUCTURE  :") == "STRUCTURE  : BULLISH TREND"
    assert _line(panel, "VOLATILITY :") == "VOLATILITY : HIGH VOLATILITY"
    assert _line(panel, "VOLUME     :") == "VOLUME     : BULLISH VOLUME SUPPORT"
    assert _line(panel, "RISK REGIME:") == "RISK REGIME: HIGH VOLATILITY RISK"
    assert _line(panel, "MACRO TREND:") == "MACRO TREND: BULLISH"
    assert _line(panel, "STATUS        :") == "STATUS        : NEAR ZONE"
    assert _line(panel, "DECISION      :") == "DECISION      : WAIT"
    assert _line(panel, "BROAD MARKET STRESS:") == "BROAD MARKET STRESS: No"
    assert "No exit-watch flags are active right now." in panel


def test_a_measured_stress_flag_still_prints_yes():
    from core.panel_render import _stress_text
    assert _stress_text(True) == "YES"
    assert _stress_text(False) == "No"
    assert _stress_text(None) == "UNKNOWN"


# ======================================================================
# 3. The router
# ======================================================================

TREND = {"trend_health": 60.0, "trend_exhaustion": False, "momentum_divergence": False,
         "momentum_mode": "STEADY", "divergence_direction": "NONE",
         "trend_direction": "BULLISH", "trend_direction_sign": 1}
ENTRY = {"long_signal": False, "short_signal": False, "score_clipped": False,
         "long_signal_blockers": ["structure does not agree"],
         "short_signal_blockers": ["structure does not agree"]}
PROVENANCE = {"run_hash": "test-run-hash", "code_hash": "test-code-hash"}
LINEAGE = {"input_hashes": {"struct": "test-input-hash"}}


def _build(trend=None, entry=None, btc_context=None):
    from models.signal_router import SignalRouter
    return SignalRouter(engine_core=object())._build_decision_object(
        symbol="TESTUSDT", timeframe="4h",
        bias={"raw": "NEUTRAL", "score": 0.0},
        trend=dict(TREND) if trend is None else trend,
        structure={},
        entry=dict(ENTRY) if entry is None else entry,
        risk={"risk_valid": True, "risk_reason": "OK"},
        exit_data={"current_price": 1.0},
        degradation=[], provenance=dict(PROVENANCE), lineage_record=dict(LINEAGE),
        exit_watch=[], btc_context=btc_context or {"available": False},
        macro_bias="NEUTRAL", chart_path="",
    )


def test_negative_control_a_complete_input_builds_a_decision():
    out = _build()
    assert "error" not in out, out.get("error")
    assert out["entry"]["long_signal"] is False
    assert out["trend"]["exhaustion"] is False


def test_an_absent_signal_is_refused_not_recorded_as_false():
    entry = dict(ENTRY)
    del entry["long_signal"]
    out = _build(entry=entry)
    assert "error" in out and "long_signal" in out["error"], out
    assert out["provenance"] == PROVENANCE, "the refusal lost the run's provenance"
    assert out["lineage"] == LINEAGE, "the refusal lost the run's lineage"


def test_an_absent_exhaustion_flag_is_refused_not_recorded_as_false():
    trend = dict(TREND)
    del trend["trend_exhaustion"]
    out = _build(trend=trend)
    assert "error" in out and "trend_exhaustion" in out["error"], out
    assert out["lineage"] == LINEAGE


def test_an_absent_entry_number_is_recorded_as_nan_not_zero():
    out = _build()
    for key in ("score", "ema_pos_pts", "base_score", "macro_multiplier",
                "combined_multiplier", "score_ceiling"):
        assert math.isnan(out["entry"][key]), (key, out["entry"][key])
    for key in ("ev_r", "assumed_win_rate", "avg_reward_r"):
        assert math.isfinite(out["risk"][key]), (
            f"{key} comes from the decision model, which always supplies it")
    assert out["entry"]["entry_status"] == "UNKNOWN"


def test_negative_control_a_present_entry_number_survives():
    entry = dict(ENTRY, score=42.5, macro_multiplier=1.1, score_ceiling=100.0)
    out = _build(entry=entry)
    assert out["entry"]["score"] == 42.5
    assert out["entry"]["macro_multiplier"] == 1.1
    assert out["entry"]["score_ceiling"] == 100.0


BTC = {"available": True, "raw": "BEARISH", "detailed": "BEARISH", "regime": "BEARISH TREND",
       "volatility": "LOW VOLATILITY", "trend_health": 40.0, "correlation": 0.5,
       "correlation_label": "MODERATE", "beta": 1.2, "broad_market_stress": False,
       "n_observations": 120, "degraded_inputs": []}


def test_an_incomplete_btc_block_is_unavailable_not_an_error_for_the_asset():
    btc = dict(BTC)
    del btc["broad_market_stress"]
    out = _build(btc_context=btc)
    assert "error" not in out, (
        "a field missing from the Bitcoin block turned the asset's analysis into "
        f"an error: {out.get('error')}")
    assert out["btc_context"] == {"available": False}


def test_negative_control_a_complete_btc_block_passes_through():
    out = _build(btc_context=dict(BTC))
    assert out["btc_context"]["available"] is True
    assert out["btc_context"]["broad_market_stress"] is False
    assert out["btc_context"]["correlation_label"] == "MODERATE"


def test_an_absent_correlation_label_reads_not_measured():
    btc = dict(BTC)
    del btc["correlation_label"]
    out = _build(btc_context=btc)
    assert out["btc_context"]["correlation_label"] == "NOT MEASURED"


def test_the_router_reads_the_engine_output_by_subscript():
    """route_and_execute's call to _build_decision_object: every section
    of the engine's output is read directly, not with a default."""
    tree = ast.parse(_read(ROUTER))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "_build_decision_object"]
    assert len(calls) == 1, f"expected one call to _build_decision_object, found {len(calls)}"
    by_name = {kw.arg: ast.unparse(kw.value) for kw in calls[0].keywords}
    for param, key in (("bias", "bias"), ("trend", "trend"), ("structure", "structure"),
                       ("entry", "entry"), ("risk", "risk"), ("exit_data", "exit"),
                       ("degradation", "degradation"), ("provenance", "provenance"),
                       ("lineage_record", "lineage"), ("exit_watch", "exit_watch"),
                       ("btc_context", "btc_context")):
        assert by_name.get(param) == f"raw_output['{key}']", (param, by_name.get(param))


# ======================================================================
# 4. engine_core
# ======================================================================

def test_engine_core_reads_the_computed_values_directly():
    """
    Six values feed the bias and entry computations: trend_direction into the
    entry score; reversal_strength into both bias calls; and the BTC call's
    sequence, regime and volume_sentiment. Each was read with a default
    (NEUTRAL, 0, NONE, NEUTRAL STRUCTURE, NEUTRAL VOLUME). None may be again.
    """
    tree = ast.parse(_read(ENGINE))
    offending = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "get" and len(n.args) == 2
                and isinstance(n.args[0], ast.Constant)):
            key = n.args[0].value
            receiver = ast.unparse(n.func.value)
            if key in ("trend_direction", "reversal_strength"):
                offending.append(ast.unparse(n))
            if receiver == "btc_structure_obj" and key in ("sequence", "regime",
                                                           "volume_sentiment"):
                offending.append(ast.unparse(n))
    assert not offending, f"read with a default again: {offending}"
