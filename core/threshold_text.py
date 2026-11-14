"""
How a sentence prints a value it sets against a line.

ENTRY 58, found 1 November 2026 (docs/PHASE7_NEXT.md, "Found after
22 September"); the rule is the redesign draft's section 6. The panel printed
"trend strength is 75/100, below the 75 the SHORT tier needs" on a trend
health of 74.52: the ladder compared the unrounded value with the line, and
the sentence printed it with `:.0f`. A value half a point or less under a
line printed as the line itself, beside the words "below the".

The rule: no sentence rounds a compared value across its line. A value under
the line prints under it, a value over the line prints over it, and only a
value that IS the line prints as the line.

compared_value_text() is that rule. It prints the value as a whole number
when that stays on the value's own side of the line; otherwise it adds
decimals, up to two, until it does; and if two are not enough it rounds a
value under the line down and a value over it up, at two decimals. So
74.52 against 75 prints "74.5", 74.999 prints "74.99", and 75.004 prints
"75.01". models/entry_model.py's _adx_text does the round-down for ADX alone;
this is the same idea for any line.

STAGE 1 OF THE REDESIGN ADDS THIS AND NOTHING CALLS IT YET. The sentences
that quote a line are rewritten through it as their gates are written, in
stages 3 and 4; the sentences entry 58 named go with trend health in stage 5.

Decimal(repr(...)) is the float's shortest decimal form, exactly, so the
rounding here cannot be moved by binary representation: the same reason
_adx_text gives.
"""

import math
import numbers
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN


def _real(value, name):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"{name} is not a number: {value!r}")
    as_float = float(value)
    if not math.isfinite(as_float):
        raise ValueError(f"{name} is not finite: {value!r}")
    return Decimal(repr(as_float))


def _side(value, line):
    """-1 under the line, 0 on it, 1 over it."""
    return (value > line) - (value < line)


def compared_value_text(value, threshold, max_decimals=2):
    """
    `value` as a sentence prints it beside `threshold`: on the same side of
    the threshold as the value itself, with as few decimals as that takes.

    Raises ValueError for a value or threshold that is not a finite number.
    There is no text for a reading that does not exist, and the caller that
    has none must say so in its own words rather than print one.
    """
    exact = _real(value, "value")
    line = _real(threshold, "threshold")
    side = _side(exact, line)

    for decimals in range(int(max_decimals) + 1):
        step = Decimal(1).scaleb(-decimals)
        printed = exact.quantize(step, rounding=ROUND_HALF_EVEN)
        if _side(printed, line) == side:
            return f"{printed:f}"

    step = Decimal(1).scaleb(-int(max_decimals))
    rounding = ROUND_FLOOR if side < 0 else ROUND_CEILING
    return f"{exact.quantize(step, rounding=rounding):f}"
