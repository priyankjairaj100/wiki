# Independent source audit, pass 4

This audit uses source paragraphs and extraction records. It does not read answer labels or retrieval outcomes.

The reviewer is an independent language-model agent. These judgments are model-assisted, not human annotations.

## Calibration review

Calibration sources are the declared pass-4 source pool. The review may guide extraction changes before the freeze.

The review checks:

- The claimed holder and role match the stated event.
- The start date belongs to that event.
- A duration has separate start and end bounds.
- An end records an observed departure, not a planned contract expiry.
- An omitted end does not discard an explicit termination in the extracted sentence.
- Pronouns and surname aliases refer to the correct person.
- Every recorded source span matches its original offsets.
- Modeled spans do not overlap, and fallback retains all remaining source words.
- Replacement pairs express explicit succession in the same role and organization.
- A predecessor receives no invented start date.

An occurrence with no stated end has an unspecified end under the adapter's policy. It does not establish continuing real-world truth.

## Confirmation review

After the extraction freeze, select claims by a fixed hash of their claim identifiers.
Use the hash prefix `pass4-independent-source-audit-v1` and select the first 60 claims.
Exclude calibration articles from this confirmation sample.
Review the full source paragraph for each sampled claim.
Review all new cross-claim pairs when their count permits this.
Do not tune rules after observing confirmation audit outcomes.

Report literal grounding separately from semantic correctness. Exact offsets alone do not establish entailment.
Source claims may use coarse dates. Their bounds must preserve the source's calendar precision.

## Status labels

- `accept`: the stated event, subject, date bounds, and endpoints match the source.
- `reject`: a specific source contradiction, attachment error, or unsupported resolution exists.
- `uncertain`: the source does not settle the required interpretation.

The audit is not a corpus-wide extraction accuracy estimate. It does not measure recall.
