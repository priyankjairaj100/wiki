# Pass 5 source-quality repairs

Implement five bounded repairs in a distinct pass-5 adapter.
Prioritize valid source attachment and explicit endpoints before expanding extraction coverage.
All repairs below use source text alone.
None requires a large model, QA labels, or reader answers.

The frozen audit accepted 52 of 60 events, rejected five, and left three uncertain.
Eleven accepted starts omitted terminations from their source paragraphs.
These findings describe the unchanged pass-4 adapter.
They must remain recorded as confirmation results.

Locations below refer to frozen files. Copy needed helpers into pass 5; leave existing dependencies unchanged.

## 1. Require a local antecedent for pronouns

**Locations:** `pass4/extraction/source_adapter.py:23` (`subject_options`), `:32` (`subject`), `:47` (`make_record`), and `:161` (`extract_passage`).
Inherited candidates also require validation; otherwise the old extractor bypasses the repair.

Replace the article-wide pronoun assumption with a local subject chain.
Require one explicit source antecedent, allowing an intervening named subject to replace it.
Ambiguous pronouns remain unknown fallback. Do not infer gender from names.

**Pass-5 calibration cases:** Françoise Dior, claim `7ad2bb9650a10769a2a31792`, has “He” referring to Count Hubert de Mirleau.
Anson Chan, claim `a19b2c840b4de5be093943ce`, assigns her husband's police tenure to her.
Both inspected confirmation cases become pass-5 calibration examples.

**Risk:** Named mentions can be objects or organizations, rather than grammatical subjects.
Use explicit subject patterns. This prevents wrong-person filtering and misleading `source_subject` metadata.

## 2. Preserve names across abbreviation punctuation

**Locations:** `pass3/extraction/source_adapter.py:53` (`sentences`), `:88` (`clean_value`), and the `STOP` expression at `:22`.
Call sites include pass-4 `extract_clauses` at `:83` and `extract_occurrences` at `:140`.
Their value patterns at `:84`, `:105`, and `:142` also stop at periods.
Changing only sentence splitting is insufficient.

Protect recognized abbreviation periods in an offset-preserving parsing view.
Cover `St .`, `A.F.C .`, `D.C.`, and initials before another name component.
Apply the same boundaries to sentences and values. Extract literal text from original offsets.
At minimum, reject fragments ending inside abbreviations.

**Calibration cases:** Existing calibration contains Max Dehn's `St . Johns College` and a `German 3 . Liga` fragment.
Inspected confirmation adds Fatih Tekke's `Zenit St . Petersburg` and Stéphane Zubar's `A.F.C . Totton`.
Niels Annen's `Washington , D.C.` also hides a six-month term after the false boundary.

**Risk:** Protecting every period merges real sentences. Use an explicit abbreviation policy without inventing entity names.
This restores club names and exposes nearby duration constraints.

## 3. Enforce clause ownership for dates and values

**Locations:** pass-4 `make_record` at `:39`, especially guards `:44`–`:54`.
Also inspect `extract_occurrences` at `:141`–`:156` and inherited-candidate checks at `:163`–`:167`.

Require leading dates at sentence starts or explicit connective boundaries, outside preceding event modifiers.
Stop values before new finite predicates such as `and continued` or `and remained`.
Do not split ordinary organization names at every conjunction.
Leave summarized multi-role durations unmodeled without separate tenure assignments.

**Calibration cases:** The existing Dundas case dates a doctorate and rectorship separately.
Inspected confirmation adds Pachachi's merged appointment and continued Foreign Service work, claim `c1ae0146ac81cd3bad410fc6`.
Brown's `ac141279aa0e622fbdac062d` and `eeb4d588ef24d2e5c6735ff1` borrow dates from preceding events.
Purnell's `9f80943e08a26a636fc515ee` summarizes two secretary roles over one interval.

**Risk:** Verb blacklists miss new predicates and reject legitimate names.
Use bounded patterns. Never redistribute a shared interval across roles without source support.

## 4. Link explicit paragraph-level end events

**Locations:** add a pass-5 linking stage after `extract_passage` at pass-4 `:177`, before final selection at `:205`.
Existing end-cue rejection appears at `:57`, `:151`, and `:167`.
Those checks inspect only a sentence or clipped extraction.

Collect calendar-dated departures, resignations, dismissals, and term ends from complete paragraphs.
Link one compatible earlier start with the same resolved holder and role or organization.
Competing starts or ambiguous targets block attachment.
Require unique local roles for `his term` and `his position`.
Retain end spans and reasons, requiring `end.lower > start.upper`.
Keep the start excerpt unchanged; the separate end sentence remains in the source partition.

**Calibration cases:** Existing O'Farrell and Brandler examples provide directly dated end clauses.
Four inspected confirmation cases support the smallest absolute-date extension: Maguire, Hayflick, Fernie, and Nagy.
Their exact cues appear in the table below.
A separate narrow rule can handle a uniquely identified organization's explicit dissolution date.

**Risk:** Leaving an employer need not end every concurrent role.
Scheduled contract expiry and new appointments do not prove departure or exclusivity.
This repair uses the existing compiler without role-based replacement edges.

## 5. Detect bounded lifetimes when the end cannot be modeled

**Locations:** pass-4 `make_record` at `:51`, `:55`, and `:57`; paragraph linking before `extract_all` at `:205`.
Inherited candidates at `:163` also require this check.

Inspect complete paragraphs for trials, approximate durations, season ends, and unresolved relative cessation dates.
Keep uniquely matched occurrences as unknown fallback when the stated end cannot enter the compiler.
Initial patterns include `for about a year`, `for a six-month term`, and expired trials.
Do not turn bounded states into open lifecycles.
Defer relative-date arithmetic and season calendars. Uncertain start offsets can create correlated endpoints.

**Risk:** Blanket rejection removes unrelated roles. Attach each bounded cue before changing modeling status.

## The eleven omitted terminations

All rows below are newly available pass-5 calibration examples.
Their full source paragraphs remain in `confirmation/confirmation_sample.jsonl`.

| Article | Claim ID | Source end cue | Smallest justified action |
|---|---|---|---|
| Gergely Rudolf | `a6f36b28342c256ac4a2f4e0` | Contract terminated “Five days later,” after 16 March 2016 | Mark bounded and unresolved. Defer arithmetic to a separately validated extension. |
| Alexander Milošević | `6f13d375cbf6278ba1ce3a90` | Left “at the end of the year” | Preserve unknown fallback. Do not equate the planned two-year deal with actual tenure. |
| Joe Thompson | `caa48f1d38c4dcf29c4c6d71` | Trial expired without a contract | Keep the temporary occurrence unmodeled; no end date is given. |
| Bernard A. Maguire | `8d3c848cf36af48685b2bad3` | “His term ended in 1870” | Attach year-precision end to the unique 1866 presidency. |
| Sir Anthony Meyer | `b84b4a0a2544246edbc24d83` | Party “disbanded in 2001” | Attach year-precision end only after unique organization resolution. |
| Leonard Hayflick | `b6d32a4e60a508215fa7f436` | “Hayflick resigned from Stanford in 1976” | Attach year-precision end to the compatible Stanford appointment. |
| Willie Fernie | `ef89771d4e62d0918d004264` | “Fernie was sacked in October 1977” | Attach month-precision end if the manager occurrence remains unique. |
| Ferenc József Nagy | `d4db9148c3df77f8eead595d` | “He held his position until 16 January 1991” | Attach the exact day to the immediately preceding Agriculture appointment. |
| Segenet Kelemu | `703acc3bfcabb2ef2ae65092` | “for about a year” | Keep unknown fallback; approximation gives no exact independent endpoint. |
| Jim Towers | `d4383d6eeda5c48c049d7a03` | Retirement at the end of the 1967–68 season | Keep unknown fallback without an explicit season-calendar policy. |
| Niels Annen | `68fb0050c5ceb14da1720948` | “for a six-month term” after `D.C.` | Repair boundaries, then retain unknown fallback for the correlated duration. |

Four rows offer direct dated role ends.
The party-dissolution row offers a fifth endpoint after unique organization resolution.
The remaining six require bounded-state handling or a separately specified date interpretation.
These are repair opportunities, not measured gains.

## Rendering and reader-run reuse

The pass-4 renderer includes subject, relation, temporal status, start bounds, end bounds, and source text.
See `pass4/pipeline/run_matched.py:113` (`prompt_for`).
Therefore, an unchanged selected excerpt does not imply an unchanged prompt.

| Repair | Direct change | Expected prompt impact |
|---|---|---|
| Pronoun repair | Subject metadata or modeled eligibility | Selected corrected units usually change prompts. |
| Abbreviation repair | Source text, offsets, and possibly partition | Selected units change prompts; lexical rankings can change elsewhere. |
| Clause repair | Value, excerpt boundary, eligibility, or source status | Clipped or rejected selected units usually change prompts. |
| Added explicit end | Certificates and end metadata; source text can stay identical | Selected affected units gain `end_bounds`, even if their eligibility stays unchanged. |
| Bounded unresolved state | Modeling status, often fallback partition | Selected units usually change metadata or context. |
| Certificate-only provenance change | Proof witnesses or unselected claims | Reuse when complete rendered requests remain identical. |

Preserving atomic boundaries for newly unknown units can avoid unnecessary ranking changes.
That requires a declared pass-5 unit policy because the current partition merges surrounding fallback text.
It does not guarantee prompt reuse.
Abbreviation repairs can change BM25 statistics globally, so regenerate all contexts with the frozen ranking policy.
Cheap extraction and retrieval recomputation is preferable to guessing which requests changed.

Cache by exact rendered prompt and complete generation request, not claim IDs or old context signatures.
The prompt hash is created at `pass4/pipeline/run_matched.py:196`.
The canonical request hash appears at `pass3/inference/run_jsonl.py:117`.
Verify identical model weights, runtime, system message, seed, token limit, stop conditions, and response schema.
Reuse only exact matches, recording their original run identifiers and request hashes.
Generate only unmatched requests.
Do not copy an earlier answer because the question or paragraph is unchanged.
No reuse percentage can be justified before rebuilding prompts.

## Preserve confirmation history

1. Keep every pass-4 source file, manifest, audit, prediction, and raw run unchanged.
2. Create `pass5/extraction/source_adapter.py` with version `source-clause-v3` and explicit dependency hashes.
3. Declare inspected confirmation paragraphs and diagnostic examples as pass-5 calibration exposure.
4. Preserve a mapping from old claims to repaired, rejected, or newly bounded claims.
5. Test the five failure classes, literal spans, complete partitions, and pair-endpoint survival.
6. Freeze pass-5 extraction and rendering before new comparative evaluation.
7. Audit a new source sample outside all inspected source articles before using its judgments for any later development.
8. Report repeated QA evaluation as post-audit revision results, alongside the preserved pass-4 confirmation history.

Keep retrieval, budgets, reader parsing, and scoring fixed unless a repair requires an explicit protocol change.
Do not silently replace the 52/60 source-audit result with a score from its repaired examples.
A fresh source audit can assess the distinct pass-5 version.
The original pass-4 results retain their original model and source scope.

This plan does not modify code or outputs and does not run new experiments.
It uses source records and audit judgments only.
