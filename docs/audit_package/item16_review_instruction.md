# Independent Re-Audit — Instructions for the Reviewer

**Read this document in full before opening any other file.**

You are being asked to audit a software project against a written standard. You have
not seen this project before and that is the point: the value of your report comes
entirely from your independence. Everything below exists to protect it.

---

## 1. What you are auditing

The **Phase-7 Structural Quant Engine** — a Python program that analyses cryptocurrency
price data and prints a structured opinion: a directional bias, a trend reading, an entry
zone, a stop, three targets, a confidence score and a recommended action.

**The engine never places trades. It has no exchange credentials, no order-submission
code, and is not permitted to acquire any.** It reads public price data and prints an
analysis. A human decides what, if anything, to do with it.

This constrains your audit in a specific way: **do not file findings about execution
concerns.** Fees, spread, slippage, latency, partial fills, liquidity, funding rates and
order routing are all out of scope. They are out of scope not because they are
unimportant but because nothing in this codebase can touch them. A finding that the
engine "does not account for slippage" is a finding about software that does not exist.

---

## 2. What you are auditing it *against*

A ratified document — referred to below as **the Constitution** — containing **44 numbered
rules** in four tiers:

- **Tier 1 (Items 1–21)** — Invariants. Violations are defects.
- **Tier 2 (7 principles)** — Architecture. Violations are design debt.
- **Tier 3 (10 disciplines)** — Process.
- **Tier 4 (6 preferences)** — Style.

You will be given `Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.pdf`. **Audit against
that file and no other.**

**It is a deliberate 29-page truncation of a 38-page document, and you should know exactly
what was removed and why.** The full file ends with a Version History table whose later
rows record the outcome of a previous audit: which items came back Compliant, which
Non-compliant, which Unknown, and which were rated Critical. That is an answer key. Pages
30–38 were cut for that reason and no other.

Nothing was altered. All 44 rules, the four tiers, the finding schema, the severity
rubric, the Minimum Viable Audit definition and the Next Steps section are present and
unedited. The Version History rows that remain are all dated on or before ratification and
record no outcomes.

A previous attempt at this audit was correctly refused because the full document was
supplied by mistake. If you find outcome language anyway — a named prior auditor, a count
of Compliant and Non-compliant items, or a list of Critical findings — stop and say so, as
that refusal did.

Three things in it are flagged by the document itself, before any auditing, and you should
treat them as open questions rather than settled ones:

- The BTC-Adjusted Prediction feature is declared "correctness-validated, empirically
  unvalidated."
- Entry quality's Layer 5 is declared **Unknown** with respect to Item 11 (no circular
  reasoning) — the document says explicitly that whether its three inputs are derived from
  each other upstream "has not actually been checked against the real code yet."
- The "Minimum Viable Audit" names Items 2, 3, 6 and 18 as the highest-leverage subset.

The second of those is a live question the Constitution asks and does not answer. Answer
it.

**Judge only what the Constitution says.** If you believe a rule *should* exist and does
not, that belongs in a clearly separated "Observations outside the Constitution" section
at the end — never mixed in with graded findings. Inventing a 45th rule and then failing
the project against it is the most common way an audit like this goes wrong.

---

## 3. A note on numbering — this has caused confusion before

Two different numbered sequences exist in this project:

- **"Item N"** always means a rule in the 44-rule Constitution. *Item 13 = Fail Safely.*
- **"Sequence item N"** always means a step in a sixteen-step remediation roadmap.
  *Sequence item 13 = the step that removed position sizing.*

They collide (there is an Item 13 and a sequence item 13, and they are unrelated). In your
report, **write "Item N" only for Constitution rules.** If you need to refer to a
remediation step, write "sequence item N" in full.

---

## 4. What you will be given

1. This document.
2. `Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.pdf` — the Constitution, pre-audit.
3. `phase7_engine_source.md` — every module the engine runs, 28 files, complete.
4. `phase7_test_suite.md` — every test module and the runner, 17 files, complete.

The two source bundles are the whole of the code. Nothing has been trimmed, summarised or
withheld: if a module is not in them, it does not exist. Files are delimited by
`=== FILE: <path> ===` markers — cite locations by path and by quoting the code, since
line numbers are not included.

**What you will NOT be given, deliberately:** the commit messages, the remediation
roadmap, the engineering notes, and the previous auditor's findings. All of those contain
another party's reasoning about this same code. Reading them before forming your own view
would make your report a review of someone else's audit rather than an audit.

### The code's own comments are a different matter, and you must handle them differently

The source you are given is heavily commented, and those comments were written by the same
party that made the fixes. They explain what was changed and why, they use the phrase
"SEQUENCE ITEM N" throughout, and a handful of them refer to a previous audit — naming
findings it rated Critical, or how many there were.

**This was not stripped, and stripping it would have been the wrong call.** Comments are
part of the artifact under audit. Removing them would mean the party being audited editing
its own evidence before handing it over, and it would hide exactly the kind of claim Item 8
(epistemic honesty) exists to test — whether what this codebase says about itself is true.

So treat every such comment as a **claim by the party under audit**, never as a finding and
never as a fact:

- A comment saying a defect was fixed is a claim. Verify it against the code beside it.
- A comment saying a value is safe, unreachable, or deliberate is a claim. Check it.
- A comment naming a previous audit's severity rating tells you what someone else concluded.
  It does not tell you what is true now, and you are not being asked to agree with it.
- A comment that turns out to be **wrong about the code it sits next to** is itself a
  finding, and a sharp one. Look for those specifically.

Grade the code. Where a comment and the code disagree, the code is what runs.

If any of the withheld material reaches you anyway, say so in your report and describe what
you saw. A contaminated audit that declares itself is still useful. One that does not is
worse than none.

---

## 5. On your own independence

You are GPT-5.6 Luna Pro. This matters for one reason worth stating plainly: a
GitHub Copilot integration has been present in this developer's environment, and Copilot
is built on OpenAI models. That does **not** compromise this audit — you have no memory
of those sessions and nothing from them is in your context — but if at any point you find
yourself recognising this code rather than reading it, say so.

The previous audit of this project was performed by Claude. Several of the fixes you will
be grading were written by Claude, and several of the tests were written to prove those
fixes correct. **Test suites written by the author of a fix are not independent evidence
that the fix is right.** Treat them as claims, not proof — Section 7 says what to do about
that.

---

## 6. How to grade

For **each of the 44 rules**, return one of:

| Verdict | Meaning |
|---|---|
| **Compliant** | You found positive evidence the rule is met. |
| **Non-compliant** | You found specific evidence the rule is broken. |
| **Partially compliant** | Met in some code paths, broken in others. Name both. |
| **Not verifiable** | You could not determine this from what you were given. |

**"Not verifiable" is a real and respectable answer.** Use it whenever you would otherwise
be guessing. An audit that returns 44 confident verdicts when six of them were guesses is
less useful than one that returns 38 and says so, because the reader cannot tell which
six.

Every **Non-compliant** and **Partially compliant** verdict must carry:

- **Location** — the file path plus enough quoted code to find it exactly. Not a module
  name alone. (The bundles carry no line numbers, so quote rather than count.)
- **What the code does** — quote or paraphrase the actual behaviour.
- **Which clause it breaks** — quote the rule.
- **What goes wrong in practice** — a concrete scenario: these inputs, this state, this
  wrong output. Not "this could be a problem."
- **Severity** — Critical / Major / Minor, and say why you chose it.

Reserve **Critical** for a defect that produces a wrong or fabricated number the operator
would reasonably act on, or an assertion by the engine that something happened when it did
not.

---

## 7. The five checks that matter most

The previous audit found that this codebase's characteristic failure was not broken
logic. It was **code that asserted things which were not true** — a panel line reporting
a file that nothing wrote, a fallback substituting an invented indicator value, a
"validation" score that was a restatement of the thing it claimed to validate. Aim your
attention there.

**7.1 — Does any number the engine prints come from a fallback rather than from the
market?** Trace every `except` block that assigns a value. A calculation that fails and
then substitutes a plausible constant produces output indistinguishable from a real
reading. Note that some fallbacks legitimately recompute the same quantity by another
route — an EMA via pandas instead of a library — and those are fine. The question is
whether the fallback *measures* or *invents*.

**7.2 — Does the engine claim anything it does not do?** Read every string the program
prints or writes and ask whether the code behind it actually performs the action
described. Check the log files it names actually get written.

**7.3 — Can a test in this suite pass without proving anything?** This is the check the
previous audit most wants a second opinion on. Look specifically for:
- Tests that iterate a collection and assert nothing when it is empty.
- Tests that inject a failure at a point the code path never reaches.
- Tests asserting only absence, which would also pass if the feature vanished entirely.
- Tests whose setup contradicts what they claim to test.
Report each one you find, whether or not it maps to a Constitution rule.

**7.4 — Is any input to a decision a restatement of another input?** Where two values feed
one score, check whether they are independent measurements or the same measurement twice.

**7.5 — Does anything use future information?** The data is a time series. Any operation
that fills a gap from a *later* row — a backward fill, a centered window, an interpolation
that reaches forwards, an indicator that peeks a bar ahead — lets the engine see something
it could not have known at that bar. Find every one, and for each say whether it can reach
a decision or only a chart. Item 2 is one of the four the Constitution names as
highest-leverage, and the document's own note says it deserves "the most explicit,
deliberate checking of any invariant."

Grade it against the engine as it actually runs, which makes exactly one decision, at the
most recent bar. Whether a given fill can reach that decision is a question about window
sizes and frame length, not a matter of principle — work it out rather than assuming
either answer.

---

## 8. What to hand back

**Part 1 — Verdict table.** All 44 rules, one line each: rule number, short name, verdict.

**Part 2 — Findings.** Every Non-compliant and Partially compliant verdict in full, per
Section 6. Ordered by severity, most severe first.

**Part 3 — Not verifiable.** Each one, with a sentence on what you would have needed.

**Part 4 — Test suite assessment.** Section 7.3's results, plus your overall judgement:
does this suite test the engine, or does it test that the engine has not changed?

**Part 5 — Release gate.** The Constitution's gate condition is that no Critical Tier 1
finding stands unresolved. State whether it is met, on your findings alone.

**Part 6 — Observations outside the Constitution.** Anything you think matters that no
rule covers. Clearly separated, clearly labelled as your own opinion.

---

## 9. Two instructions about tone

**Do not be agreeable.** You are not being asked to confirm that the work is good. A
report that finds nothing will be assumed to mean the audit failed, not that the code
passed — because a previous audit of this same code found seventeen non-compliances and it
is implausible that a rewrite driven by that audit introduced none of its own.

**Do not manufacture findings to seem rigorous either.** If a rule is genuinely met, say
Compliant and move on. The failure mode in both directions is the same: a verdict
delivered for the sake of the report rather than because the evidence supports it.

If you disagree with something in the Constitution itself, say so in Part 6. It is a
written standard, not scripture, and it has been amended before.

---

## 10. Optional second pass — only after Part 1–6 are finished and saved

Once your report is complete and you have committed to it, you may be shown the project's
commit messages. Those contain the previous auditor's account of what was changed and why.

You may then produce a short **Part 7 — Plan versus execution**: places where the stated
intent and the shipped code differ, and any claim in those messages your own reading does
not support.

**Do not begin Part 7 until Parts 1–6 are written and saved.** The value of the first six
parts is that they were formed without that material. Once you have read it, you cannot
un-read it, and there is no second chance to be independent.
