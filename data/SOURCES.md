# Data sources and provenance

These public inputs contain no proprietary, employer or partner data. All three local CSVs
are now **byte-for-byte source snapshots**, including the `title` field in exposure data.
No input transformation is applied on disk. Cleaning happens in `analysis.py`.

## Frozen source and verification

- Dataset: [Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex).
- Immutable revision: `4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6`.
- Download verification / repair date: **November 11, 2026**. The original repository
  retrieval date is unknown; this is not a claimed original collection date.
- [input_manifest.json](input_manifest.json) records each immutable URL, SHA-256 hash,
  publication date, row count and exact CSV column list. `provenance.py` checks hashes and
  complete rows before any analysis. Tests require deliberate baseline updates.
- `python scripts/restore_inputs.py` restores only these pinned snapshots and verifies
  every source hash before replacing local files. Analysis and tests work offline.

## 1. `job_exposure.csv`: March 2026 observed exposure

- Source path: `labor_market_impacts/job_exposure.csv`; **756 occupations**.
- Method: [Massenkoff and McCrory, March 5, 2026](https://www.anthropic.com/research/labor-market-impacts).
- Definition: theoretical task feasibility plus observed work-related Claude usage;
  automated use receives full weight and augmentative use half weight, with task coverage
  aggregated by time spent. It includes Claude.ai and API evidence. It is a composite
  coverage measure, not raw task presence, conversation share, or a labor-market outcome.
- The publication combines evidence from preceding Economic Index reports. Its March 2026
  publication date is distinct from the dates of underlying usage observations; it is not
  the February 2025 release.
- Fields: `occ_code` (six-digit SOC), `title`, `observed_exposure` (0–1).
- Publisher licence: CC-BY, per the [dataset licence statement](https://huggingface.co/datasets/Anthropic/EconomicIndex/blob/4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6/README.md).

## 2. `automation_vs_augmentation.csv`: February 2025 collaboration mix

- Source path: `release_2025_02_10/automation_vs_augmentation.csv`; **six rows**.
- Method: [February 2025 release documentation](https://huggingface.co/datasets/Anthropic/EconomicIndex/blob/4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6/release_2025_02_10/README.md).
- Augmentation = learning + task iteration + validation; automation = directive + feedback loop.
- The rows sum to approximately 84.2%: `none` is 2.9%, and 15.8% is outside represented
  categories. The reported 57.4 / 42.6 split uses only the five named types, approximately
  81.3% of conversations, as its denominator.
- It has no occupation dimension. It cannot be broken out by wage quintile or the matched
  sample, and must not be treated as contemporaneous with the March 2026 exposure measure.
- Publisher licence: CC-BY.

## 3. `wage_data.csv`: legacy O*NET scrape and automatability

- Source path: `release_2025_02_10/wage_data.csv`; **1,090 complete rows**.
- Anthropic's release documentation identifies wages as an O*NET website scrape produced
  with [adamkq/onet-dataviz](https://github.com/adamkq/onet-dataviz).
- The entire upstream CSV is byte-identical to [`jobData.csv` at commit 475e860e40cd7b09e4946f228eff270689a82fdc](https://github.com/adamkq/onet-dataviz/blob/475e860e40cd7b09e4946f228eff270689a82fdc/jobData.csv),
  committed **January 20, 2020**. Both SHA-256 hashes are
  `4453fc56402c94306e4749ad62b6f7c313f63d884ca99bab767a52e7d627b15f`.
  It cannot be a May 2024 wage snapshot, as previously stated here.
- **Verified wage spot checks:** Accountants and Auditors = $70,500 in the
  [BLS May 2018 table](https://www.bls.gov/oes/2018/may/oes132011.htm);
  Actuaries = $102,880 in the [BLS May 2018 table](https://www.bls.gov/oes/2018/may/oes152011.htm).
  These establish the vintage of checked values, not every row. The scrape has no uniform
  reference-year field, so a single year for the full table remains **unverified**.
  Wages are nominal legacy values, not current or inflation-adjusted salaries.
- The scraper's README identifies `ChanceAuto` as scraped from willrobotstakemyjob.com,
  with −1 for unavailable matches. Treat it as a legacy predicted-automatability score;
  it is not an observed generative-AI automation rate.
- Cleaning retained from the original analysis: values of `MedianSalary` below 1,000 are
  assumed hourly and multiplied by 2,080; negative `ChanceAuto` is missing and the rest
  divided by 100; O*NET subcodes collapse to six-digit SOC by median. These conventions
  and the six-digit join do not resolve SOC-version differences.
- Publisher licence: CC-BY for the distributed dataset; underlying U.S. government wage
  and O*NET material is public domain. This repository does not relabel the combined CSV
  as wholly public-domain material.

## Join coverage and correction

The complete wage snapshot collapses to 821 six-digit occupation codes; 672 match the 756
exposure occupations with valid wages, leaving 84 unmatched. Their mean exposure (0.1325)
exceeds the matched mean (0.0700). This comparison describes the occupation-wide mean;
it does not establish a bias direction for wage quintiles or the wage gradient, because
missing occupations cannot be assigned wages from this table.

`ChanceAuto` is missing for another 89 matched occupations. The two score columns have
different denominators. Computer and Mathematical (n = 5) and Legal (n = 7) group means
are based on thin samples. Analysis prints coverage and writes it to `results.json`.

[CORRECTIONS.md](../CORRECTIONS.md) documents the repaired truncation and two exposure
values, along with before/after results. The previous inputs remain available in Git
history; they are not redistributed here as an alternative valid source snapshot.
