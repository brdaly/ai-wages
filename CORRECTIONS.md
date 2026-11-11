# Input and interpretation correction — November 11, 2026

This working correction replaces the baseline at commit
`f8873f272497ccc36fe29e0d827db6a0db0677aa`. It has not created a GitHub release.
The previous inputs and results remain in Git history.

## What source verification found

1. The previous `wage_data.csv` contained 702 complete records and a partial 703rd
   (`15-1142.00,Network`). It was an exact prefix of the complete upstream file, which
   has 1,090 complete records. The partial row was treated as missing by pandas and dropped.
2. Two exposure rows differed from the immutable upstream source with no recorded
   transformation: SOC 29-1131 was 0 instead of 0.0926; SOC 29-2033 was 0 instead of 0.0513.
3. The exposure file belongs to the March 2026 hybrid observed-exposure methodology,
   rather than the February 2025 raw-usage framing used in the earlier prose.
4. The wage file is byte-identical to an O*NET scrape committed in January 2020.
   Checked wage values match May 2018 BLS medians; a uniform year is unverified.
   The prior May 2024 attribution was unsupported.

All three local inputs now match upstream bytes at revision
`4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6`, including the exposure title column.
`data/input_manifest.json` records hashes, row counts, immutable URLs and the November 11
verification date. No on-disk transformations or silent substitutions remain.

## Before and after

The original and corrected analysis use the same wage normalization, subcode aggregation,
join, correlation and binning methods. These changes repair the inputs and their description;
they do not introduce a new SOC crosswalk, wage survey, weighting scheme or robustness study.

| Quantity | Previous | Corrected |
|---|---:|---:|
| Matched occupations | 454 | 672 |
| Collapsed wage occupations | 554 | 821 |
| Unmatched exposure occupations | 302 | 84 |
| Matched mean exposure | 0.0717 | 0.07 |
| Unmatched mean exposure | 0.0844 | 0.1325 |
| Pearson wage–exposure r | 0.197 | 0.169 |
| Spearman wage–exposure ρ | 0.333 | 0.288 |
| Missing legacy automatability | 73 | 89 |

| Quintile | Median wage, previous → corrected | Exposure, previous → corrected | Legacy score, previous → corrected |
|---|---:|---:|---:|
| Q1 (lowest pay) | $27,730 → $28,260 | 0.0372 → 0.0378 | 0.7174 → 0.7447 |
| Q2 | $38,750 → $38,055 | 0.0562 → 0.0566 | 0.7119 → 0.7041 |
| Q3 | $49,500 → $48,270 | 0.0657 → 0.0557 | 0.4585 → 0.5665 |
| Q4 | $63,340 → $62,340 | 0.0975 → 0.0949 | 0.3478 → 0.3948 |
| Q5 (highest pay) | $92,250 → $91,130 | 0.1019 → 0.1051 | 0.1444 → 0.1766 |

The positive association remains modest, with a smaller correlation. Quintile means now
dip slightly from Q2 to Q3, so the earlier strictly monotonic description is removed.
The highest-ranked matched occupations and group counts also change. Every major-group
row is regenerated in `results.json`; the README, findings and figure use corrected values.

The separate February 2025 collaboration input is unchanged: approximately 57.4%
augmentation and 42.6% automation within the five named interaction categories. It is
not a statistic for the matched occupations or the exposure measure's vintage.

## Verification and limits

The original baseline was reproduced before replacing the inputs. The corrected analysis
runs from committed data only. Checksum and complete-record validation now precede analysis;
regression tests reject edited/truncated inputs and compare every published result to
`results.json`. Exact dependencies and CPython 3.12.14 are recorded for a tested environment.
Chart labels and occupation titles now follow the source measure and its own title field.

Provenance is documented in [data/SOURCES.md](data/SOURCES.md). The unknown uniform wage
vintage, SOC-version differences, selected join sample, distinct score denominators,
unweighted occupation averages and lack of causal identification remain limitations.
This correction does not claim that reproducibility establishes research validity.
