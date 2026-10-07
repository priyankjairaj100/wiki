# Restored final source audit

This audit evaluates the final frozen source adapter. It uses only extraction records and their original source paragraphs.
The reviewer is a language-model agent. These are model-assisted judgments, not human annotations.
Earlier unsaved audit records were lost during workspace maintenance. Their reported counts are not reused.
The complete membership of that lost audit is unavailable. Its prior exposure cannot be fully reconstructed.
This is a new recorded audit. It is not a guaranteed previously unseen sample.

## Freeze and selection

1. Freeze the adapter and its development and test extraction outputs before selecting this sample.
2. Exclude every article in the saved calibration pool and completed earlier source reviews.
3. Also exclude articles identifiable from the summary of the lost audit.
4. Select 20 development claims and 40 test claims by increasing SHA256 of `pass5-restored-independent-source-audit-v1`, a null byte, the split, a null byte, and the claim identifier.
5. Freeze the membership and all input hashes before reviewing full source paragraphs.
6. Keep the adapter fixed after reading this audit.

No current benchmark questions, answer labels, retrieval outcomes, or reader outputs enter selection or review.
Previously generated inventories without completed judgments do not count as completed reviews.
The saved exposure registry records all included paths and hashes.

## Review fields

Read the complete source paragraph for every sampled claim.
Check each literal span against its recorded offsets.
Check the subject, predicate, role or location, and start-date attachment.
Check each supplied end separately from the core event.
Check whether the full paragraph contains an explicit omitted end for the same event.
A missing calendar date does not establish an observed end date.
A contract duration does not establish a completed tenure unless the text states that tenure.
An unrelated role change does not necessarily end another role.

Use `accept` when the source supports the modeled field.
Use `reject` when a specific contradiction or unsupported interpretation exists.
Use `uncertain` when the source does not settle the interpretation.
Report core-event judgments, supplied-end judgments, and omitted-end judgments separately.
Explain every reject or uncertain judgment with a precise source statement.
These results do not estimate corpus-wide precision or extraction recall.
