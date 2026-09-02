# Independent Re-Audit, Round 2 — Instructions for the Reviewer

**Read this document in full before opening any other file.**

You are being asked to audit a software project against a written standard. Everything
below exists to protect the value of your report, which comes from your independence and
from your willingness to say what you actually find.

---

## Revision history

| Rev | Date | Change |
|---|---|---|
| 1 | 30 August 2026 | Issued for the first independent re-audit. |
| 2 | 2 September 2026 | Reissued for a second round on a different model. Section 5 rewritten with the independence position stated honestly, including a disclosure that Rev 1's audit was run on a model that was not on the clean list. Section 4 gains version-control history, a generated manifest, project files and execution transcripts. New Section 4a states plainly what this round can and cannot be. New check 7.6. Section 11 explains how to request runs. |
| 3 | 2 September 2026 | Reissued after two attempts at Round 2 ended without a report. The Constitution now ships as text rather than PDF, because the second attempt reached a model that could see the file's name and none of its contents (Section 2). Section 2's stop condition is scoped, resolving a contradiction with Section 9 that a reviewer raised. Section 5 gains a model-identity check and a fourth disclosure covering the two failed attempts. |

Revs 1 and 2 are preserved unedited at `docs/audit_package/item16_review_instruction.md`
and `docs/audit_package/item16_review_instruction_rev2.md`. This document supersedes both
and is self-contained: you do not need to read either.

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

You will be given `Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt`. **Audit against
that file and no other.**

**It is text rather than PDF for one reason, and you should know it.** The previous attempt
at this round sent the PDF. The reviewing model could see the filename and none of the
contents, said so, and stopped — which was the right thing to do. Rather than ask a
reviewer to work around a standard they cannot read, the format was changed. The extraction
was produced mechanically with `pdftotext -layout`; the file's own header carries the source
PDF's SHA-256, its page count, and the completeness checks run before it was sent. Nothing
was edited, reordered, summarised or omitted. Layout extraction does leave artefacts —
footnote markers land against the word they annotate, so you will read "Determinism6" and
"Fail Safely14" — and those are artefacts of the extraction, not of the standard. If
anything in it reads as damaged rather than merely awkward, say so.

**It is a deliberate 29-page truncation of a 38-page document, and you should know exactly
what was removed and why.** The full file ends with a Version History table whose later
rows record the outcome of a previous audit: which items came back Compliant, which
Non-compliant, which Unknown, and which were rated Critical. That is an answer key. Pages
30–38 were cut for that reason and no other.

Nothing was altered. All 44 rules, the four tiers, the finding schema, the severity
rubric, the Minimum Viable Audit definition and the Next Steps section are present and
unedited. The Version History rows that remain are all dated on or before ratification and
record no outcomes.

An earlier attempt at this audit was correctly refused because the full document was
supplied by mistake. If you find outcome language **in the Constitution file, or in either
of the two code bundles** — a named prior auditor, a count of Compliant and Non-compliant
items, or a list of Critical findings — **stop and say so, as that refusal did.** You will
not be penalised for refusing. You would be doing the job.

That scope is deliberate and it matters. *This* document refers to earlier rounds openly:
Section 4a explains what they cost you, Section 5 names the model that ran Rev 1, and
Section 9 gives raw counts of what previous rounds returned. None of that is a leak and
none of it should stop you — the instruction is allowed to tell you that findings existed,
because knowing a number tells you nothing about which rules failed. What must not reach
you before you have graded is the *content*: which item, which verdict, which severity. If
you find that anywhere, in any file, stop.

Three things in it are flagged by the document itself, before any auditing, and you should
treat them as open questions rather than settled ones:

- The BTC-Adjusted Prediction feature is declared "correctness-validated, empirically
  unvalidated."
- Entry quality's Layer 5 is declared **Unknown** with respect to Item 11 (no circular
  reasoning) — the document says explicitly that whether its three inputs are derived from
  each other upstream "has not actually been checked against the real code yet."
- The "Minimum Viable Audit" names Items 2, 3, 6 and 18 as the highest-leverage subset.

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
2. `Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt` — the Constitution, pre-audit, as
   text. Section 2 says why it is text and not PDF. The PDF itself remains in the
   repository at `docs/audit_package/`, and is deliberately **not** in this package:
   shipping two files that both claim to be the standard is the same defect check 7.6
   asks you to look for, and it would be poor form to commit it in the packaging while
   grading the code for it.
3. `phase7_engine_source.md` — every module the engine runs, complete, plus the
   project files that decide how it is built and pinned (`pytest.ini`,
   `requirements.txt`, `requirements-dev.txt`, `.gitattributes`, `.gitignore`).
4. `phase7_test_suite.md` — every test module and the runner, complete.
5. `MANIFEST.md` — file counts and a SHA-256 for every file in the two bundles.
6. `version_control_history.md` — the shape of the repository's history.
7. `execution_transcripts.md` — output the engine actually produced when run.

Items 3 through 6 are **generated by a script**, `docs/build/build_audit_package.py`,
which walks the repository and computes the manifest from the bytes it wrote. Rev 1's
package was assembled by hand and a false claim got into it as a result. You can verify
completeness yourself: hash any file in a bundle and compare it against `MANIFEST.md`. If
they disagree, the package was altered after it was built, and you should say so.

### The version-control history, and what was held back from it

Five rules came back **Not verifiable** in Rev 1's audit for one reason only: commit
history was withheld, so questions about version control, controlled changes, known-good
checkpoints, rollback and documentation of decisions could not be answered from what was
supplied. That was a defect in the package, not in the project, and it is fixed here.

`version_control_history.md` carries hashes, dates, authorship, every file changed with
insertions and deletions, plus branches, tags and whether the working tree is clean.
**Commit subject lines and bodies are deliberately withheld from it.** A subject like
"Audit Findings 6 and 7: make a run reconstructable and traceable" leaks a finding number
and its outcome in eleven words. The full messages are in
`commit_messages_PART7_ONLY.md`, for the optional Part 7 pass described in
Section 12 — **do not open that file until Parts 1 through 6 are written and saved.**

### The code's own comments and the tests' own docstrings

The source is heavily commented and the tests carry long explanatory docstrings. Both were
written by the party that made the fixes. They use the phrase "SEQUENCE ITEM N" throughout,
and **many of them describe, in detail, defects a previous audit found and how they were
fixed.**

**None of this was stripped, and stripping it would have been the wrong call.** Comments
and docstrings are part of the artifact under audit. Removing them would be the party being
audited editing its own evidence before handing it over, and it would hide exactly the kind
of claim Item 8 (epistemic honesty) exists to test — whether what this codebase says about
itself is true.

So treat every such comment as a **claim by the party under audit**, never as a finding and
never as a fact:

- A comment saying a defect was fixed is a claim. Verify it against the code beside it.
- A comment saying a value is safe, unreachable, or deliberate is a claim. Check it.
- A comment naming a previous audit's severity rating tells you what someone else
  concluded. It does not tell you what is true now, and you are not being asked to agree.
- A docstring narrating how a defect was discovered is a claim about history, and the
  history is not what you are grading. The code is.
- A comment or docstring that turns out to be **wrong about the code it sits next to** is
  itself a finding, and a sharp one. Look for those specifically.

Grade the code. Where a comment and the code disagree, the code is what runs.

---

## 4a. What this round can be, and what it cannot

Be clear-eyed about this, because your report should be.

Rev 1's audit was a genuine blind review: the auditor received source, tests and the
standard, and nothing about what anyone had previously concluded. **This round is not
that, and cannot be.** In the week since, the fixes for Rev 1's findings shipped with
extensive comments and docstrings describing what was found and what was changed. Those are
part of the artifact and are in your bundles.

So you are not being asked to independently re-discover Rev 1's findings. You could not,
and a report claiming to have done so would be wrong. What you are being asked for is two
things, and they are worth more than the thing that is no longer available:

**One — are the claimed fixes real?** The codebase asserts, in dozens of places, that a
specific defect was closed in a specific way. Every one of those is a testable claim about
code sitting immediately beside it. A fix that was described but not made, or made
incompletely, or made in a way that introduced a new problem, is the highest-value finding
you can return.

**Two — what did neither round find?** Rev 1 read the code. So did four earlier review
passes across three other models. Between them they missed a defect that was later found by
running the program. Sections 7.6 and 11 are about that.

If at any point you find yourself agreeing with a claim in a comment because it is stated
confidently rather than because you checked it, that is the failure mode this section
exists to name.

---

## 5. On your own independence — stated honestly

You are **Qwen3.8-Max**. If you are not — a different model, or a different version —
say so in the first line of your report and then carry on with the audit. The ledger
described below is worth exactly what that check is worth, and the project has no way to
run it from its side.

This project keeps a written ledger of which model families have
seen which documents, on the principle that a model which has read the standard is no
longer independent when grading against it, and that independence is tracked at the
laboratory rather than at the checkpoint — a newer model from a family that has already
worked on the artifact is not an independent reviewer of it.

You are on the clean list. Several stronger models are not, and you should know that this
is why you were chosen: of the five highest-ranked coding models available at the time of
writing, three are Claude models (Claude wrote this engine and its fixes), one shares a
lineage with the reviewer who ran Rev 1, and one was spent on an earlier attempt at this
same audit. **You were selected for independence, not because you outrank the
alternatives.** Grade accordingly: the value of your report is in its impartiality, so do
not try to compensate by being either generous or harsh.

Four disclosures, because a ledger that only records the convenient facts is not a ledger.

**Rev 1's auditor was not on the clean list.** The project's own remediation plan, written
the day before, had considered that model and rejected it for a different step because it
had already read the Constitution during an earlier hostile review. Step 8 was then run on
it anyway. The findings were verified against source before anything was fixed and are
believed sound, but the project has recorded that its prior re-audit was contaminated. You
are not being asked to agree with that audit, and — see Section 4a — you will not be given
its report before you write yours.

**This repository is public on GitHub, and has been for some time.** Any model trained
since then may have this codebase in its weights. The project's ledger tracks what models
were shown in conversation; it does not and cannot track training data. This applies to you
as much as to anyone. **If at any point you find yourself recognising this code rather than
reading it, say so in your report.** That is not a failure and it will not invalidate your
work — an undisclosed prior exposure would.

**This round has been attempted twice already, and neither attempt produced a report.**
The first ended in repeated provider-side failures before grading began. The second reached
a model that could see the Constitution's filename and none of its contents, said so, and
stopped; that is why the standard now reaches you as text. No findings came back from
either, and nothing from either has been carried into this document. If you are the same
model as one of those attempts, this is a fresh conversation and none of that material is
in your context — the project's position is that session exposure ends with the session,
while training and lineage exposure never do.

**Claude wrote the fixes you are grading, and wrote the tests that check them.** A test
suite written by the author of a fix is not independent evidence that the fix is right.
Treat the suite as a set of claims, not as proof — Section 7.3 says what to do about that.

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
less useful than one that returns 38 and says so, because the reader cannot tell which six.

Note that Section 4 now supplies version-control history. Rules about process discipline
that were previously unanswerable should now be gradeable — but grade them on the evidence
supplied, and if that evidence is still insufficient, say Not verifiable and say what was
missing.

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

## 7. The six checks that matter most

This codebase's characteristic failure has never been broken logic. It is **code that
asserts things which are not true** — a panel line reporting a file that nothing wrote, a
fallback substituting an invented indicator value, a "validation" score that was a
restatement of the thing it claimed to validate, an action label naming a direction its own
risk levels contradicted. Aim your attention there.

**7.1 — Does any number the engine prints come from a fallback rather than from the
market?** Trace every `except` block that assigns a value. A calculation that fails and
then substitutes a plausible constant produces output indistinguishable from a real
reading. Note that some fallbacks legitimately recompute the same quantity by another
route — an EMA via pandas instead of a library — and those are fine. The question is
whether the fallback *measures* or *invents*.

**7.2 — Does the engine claim anything it does not do?** Read every string the program
prints or writes and ask whether the code behind it actually performs the action described.
Check that the files it names actually get written, and that a claim is conditional on the
write having succeeded rather than on the attempt having been made.

**7.3 — Can a test in this suite pass without proving anything?** This is the check the
project most wants a second opinion on, and the previous auditor's judgement of the suite
was that "it tests that selected implementation details have not changed more strongly than
it tests whether the engine is correct." Look specifically for:
- Tests that iterate a collection and assert nothing when it is empty.
- Tests that inject a failure at a point the code path never reaches.
- Tests asserting only absence, which would also pass if the feature vanished entirely.
- Tests whose setup contradicts what they claim to test.
- Tests that return instead of skipping, so an unmet precondition reports as a pass.
- Tests whose fixture can no longer produce the condition the test was written for.
Report each one you find, whether or not it maps to a Constitution rule.

**7.4 — Is any input to a decision a restatement of another input?** Where two values feed
one score, check whether they are independent measurements or the same measurement twice.
Check also whether a factor already weighted inside a composite is then applied a second
time on top of it.

**7.5 — Does anything use future information?** The data is a time series. Any operation
that fills a gap from a *later* row — a backward fill, a centered window, an interpolation
that reaches forwards, an indicator that peeks a bar ahead — lets the engine see something
it could not have known at that bar. Find every one, and for each say whether it can reach
a decision or only a chart. Grade it against the engine as it actually runs, which makes
exactly one decision, at the most recent bar. Whether a given fill can reach that decision
is a question about window sizes and frame length, not a matter of principle — work it out
rather than assuming either answer.

**7.6 — Do two modules ever compute the same thing from different sources, without
anything comparing them?** This is the new one, and it is here because it is how the most
serious defect since Rev 1 got through both a full audit and a large test suite.

Look for a quantity that is derived independently in more than one place — a direction, a
threshold, a state, a count — and ask what happens when the two disagree. Then ask what in
the code would notice. A disagreement that nothing checks is not a hypothetical: it is a
defect waiting for the inputs that produce it.

Pay particular attention to conditions that only arise when two data sources point
different ways, because a test suite built on fixtures cannot reach a state its fixtures
never enter. Ask of any invariant: **what input would break this, and does any fixture in
the suite produce that input?** If the answer to the second question is no, the invariant
is unproven however many tests appear to cover it.

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

Add to Part 6, if you have anything to say about them, two things this round specifically
wants: **claimed fixes you could not confirm**, and **any place where you noticed yourself
relying on a comment rather than on the code**.

---

## 9. Two instructions about tone

**Do not be agreeable.** You are not being asked to confirm that the work is good. A report
that finds nothing will be assumed to mean the audit failed, not that the code passed —
because a previous audit of this same code returned seventeen non-compliances, a later one
returned fifteen findings including five rated Critical, and a sixteenth Critical was found
after that by running the program. It is implausible that a week of remediation driven by
those introduced none of its own. **The counts are given; the content is not, and you
should not ask for it before Part 7.**

**Do not manufacture findings to seem rigorous either.** If a rule is genuinely met, say
Compliant and move on. The failure mode in both directions is the same: a verdict delivered
for the sake of the report rather than because the evidence supports it.

If you disagree with something in the Constitution itself, say so in Part 6. It is a
written standard, not scripture, and it has been amended before.

---

## 10. If something is missing or contradictory

Say so rather than working around it. Three specific cases:

- **A file you need is absent.** The manifest lists everything that shipped. If a module is
  imported and not present, that is either a packaging error worth reporting or a defect in
  the code worth reporting; say which you think it is.
- **The Constitution contradicts itself.** It has done before, and the contradiction was
  recorded rather than repaired. Report it as a DEFECT observation and grade against the
  reading you find more defensible, saying which you chose and why.
- **You are asked to grade a rule that does not apply to software of this kind.** Say so.
  Do not stretch a rule to produce a verdict.

---

## 11. You cannot run this code, and that has already cost one audit

You are receiving source, not a runnable environment. Be aware of what that costs, because
it is not theoretical here.

The most recent Critical in this project was invisible to reading. It appeared only when two
data sources pointed in opposite directions — a state that arises regularly in live markets
and that no fixture in the test suite produced. Four review passes across three model
families, plus a full independent audit, all read the code and did not find it. It surfaced
on the first run against live data.

`execution_transcripts.md` contains output the engine actually produced, captured
verbatim. **Treat it exactly as you treat comments: as claims by the party under audit.** It
was produced and selected by the party being graded, and a transcript proves what happened
on one run, not what happens generally.

**You may request specific runs.** If reaching a verdict would be easier with the program's
actual behaviour under some condition — a particular input shape, a forced failure, a
degraded state — say so precisely, in a clearly marked section at the end of your report:
the condition, and what output would distinguish the possible answers. Those runs will be
executed verbatim and the raw output returned to you, without editing.

Requesting a run does not weaken your report. Reaching a confident verdict on a question
that needed one does.

---

## 12. Optional second pass — only after Parts 1–6 are finished and saved

Once your report is complete and you have committed to it, you may open
`commit_messages_PART7_ONLY.md`. It contains the fixer's own account of what was
changed and why, and names findings from previous audits along with their severities.

You may then produce a short **Part 7 — Plan versus execution**: places where the stated
intent and the shipped code differ, and any claim in those messages your own reading does
not support.

**Do not begin Part 7 until Parts 1–6 are written and saved.** The value of the first six
parts is that they were formed without that material. Once you have read it, you cannot
un-read it, and there is no second chance to be independent.
