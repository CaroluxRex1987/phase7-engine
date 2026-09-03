# Instruction — Reviewing the Phase-7 Engineering Constitution

Give this to any reviewer asked to critique the Constitution itself.
Paste it above the document.

---

## What you are reviewing

A governing document for one software project: 44 numbered rules in four
tiers. You are reviewing **the document** — whether its rules are sound,
complete, consistent, and capable of being checked.

You are **not** auditing code. You will not be shown any.

## What the software is, because this is where reviews go wrong

An analytical and decision-support tool. It reads public market data and helps
a trader judge an entry price, three targets, a stop, and whether the risk is
acceptable. It holds no credentials, sends no orders, and has no capacity to
execute a trade or move money.

**It is not a trading system.** A reviewer who grades this document against the
standards owed by one will produce conclusions calibrated to a product that
does not exist.

This is not hypothetical. A previous review raised latency limits, memory
bloat and race conditions for a program that fetches 450 candles, runs once,
and exits — single-threaded, no stream, no long-lived process. Ask whether a
concern applies to *this* software before raising it.

## The audit results in the Version History are a snapshot, not the present

The Version History records an audit run at ratification: ten Compliant, ten
Non-compliant, one Unknown, three Critical. **That is the state on that date.**
Remediation has happened since.

Do not describe the engine's current condition from those rows, and do not
treat "unresolved at ratification" as "unresolved now."

## What is useful

1. **Contradictions.** Two clauses that cannot both be followed. Quote both.
2. **Rules that cannot be checked.** Name the rule, and say what would make it
   verifiable.
3. **Gaps that matter for this kind of software.** Not for software in
   general.
4. **Rules that are wrong** — ones that would make the project worse if
   followed as written.

## What is not useful

- Requirements imported from a generic checklist without asking whether they
  apply here.
- Praise. It has been solicited before and it was worth nothing.
- Anything about the code. You have not seen it.
- Any recommendation that would stop the author running the program. The
  release gate deliberately restricts *relying on output for a real trading
  decision*, not *running the software*. Two of this project's most serious
  defects were found by running it and reading the output. A rule that blocks
  running it blocks fixing it.

## Form

For each point: which item or section, what is wrong with it, and what it
should say instead.

If you propose a change, **state what it weakens as well as what it
improves.** Every amendment to this document must name its own cost; a
proposal that only lists benefits cannot be adopted.

Be direct. Disagreement is the reason you were asked.

**If you cannot see the contents of the attached document — if you can read
its filename but not its text — say so and stop.** That has happened before
and cost a full review round.

## Independence

This is not an audit and does not require an independent reviewer.

But note the consequence: reading this document means you can no longer serve
as an independent auditor of the engine against it. The project tracks that
and accepts it here.
