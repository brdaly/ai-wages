# Data sources & provenance

All inputs are public. No proprietary, employer, or partner data is used in this repository.

## 1. `job_exposure.csv` — observed AI exposure by occupation
- **Source:** Anthropic Economic Index, `labor_market_impacts/job_exposure.csv`
- **URL:** https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/labor_market_impacts/job_exposure.csv
- **License:** CC-BY 4.0
- **Fields:** `occ_code` (6-digit SOC), `title`, `observed_exposure` (0–1; share of the occupation's O\*NET tasks observed in Claude.ai usage). Title column dropped in the local copy; values unchanged.

## 2. `automation_vs_augmentation.csv` — collaboration mix
- **Source:** Anthropic Economic Index, `release_2025_02_10/automation_vs_augmentation.csv`
- **URL:** https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/automation_vs_augmentation.csv
- **License:** CC-BY 4.0
- Augmentation = learning + task iteration + validation; Automation = directive + feedback loop.
- **Denominator.** The file's six rows sum to 84.2%, not 100%: `none` accounts for 2.9%, and the
  remaining 15.8% of conversations fall outside these categories and have no row in the file at
  all. The reported 57/43 split is computed over the 81.3% carrying one of the five named
  interaction types — so it is a share *of classified interactions*, which is roughly four in
  five conversations, not of all usage.
- **Scope.** This file has no occupation dimension. It is six global rows over Claude.ai
  conversations, so the split cannot be broken out by occupation, wage quintile, or the 454
  occupations analysed elsewhere in this repository.

## 3. `wage_data.csv` — wages + legacy automatability
- **Source:** Anthropic Economic Index, `release_2025_02_10/wage_data.csv` (bundles BLS median wages and a published Frey-&-Osborne-lineage automation-probability index).
- **URL:** https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/wage_data.csv
- **Fields used:** `SOCcode` (O\*NET-SOC), `JobFamily` (SOC major group), `MedianSalary`, `ChanceAuto` (0–100; −1 = missing).
- **Cleaning:** `MedianSalary` < 1000 treated as hourly → ×2080; `ChanceAuto` of −1 set to missing then scaled to 0–1; O\*NET sub-codes collapsed to base 6-digit SOC by median.

## Underlying public references
- BLS Occupational Employment and Wage Statistics (OEWS), May 2024 — https://www.bls.gov/oes/
- O\*NET task statements & SOC structure — U.S. Department of Labor (public domain)
- Brynjolfsson, Li & Raymond, *Generative AI at Work*, NBER w31161 / QJE 140(2), 2025

## Join coverage

`job_exposure.csv` and `wage_data.csv` are joined on 6-digit SOC with an inner join, which is a
selection step worth recording alongside the provenance:

| | Occupations |
|---|---|
| `job_exposure.csv` | 756 |
| `wage_data.csv`, collapsed to 6-digit SOC | 554 |
| Matched (the analysed sample) | 454 |
| Unmatched | 302 |

The wage table is a legacy file and has no row for the other 302. Those occupations are on
average more AI-exposed than the matched ones (0.084 vs 0.072), so the analysed sample's
occupation-wide mean sits below the full index's. That bounds the overall mean only: the dropped
occupations have no wage, so nothing here says where they would have fallen in the wage
distribution or which way they would move the gradient. `analysis.py` recomputes and prints these counts on every run
and writes them to `results.json` under `coverage`, so a change in either input surfaces rather
than passing silently.

`ChanceAuto` is additionally missing (encoded `-1`) for 73 of the 454 matched occupations, with
the gaps concentrated in the upper wage quintiles.

*Reproducibility note: the three CSVs were retrieved from the URLs above and are committed as
retrieved. `analysis.py` reads only `data/`, and fails with a pointer back to this file if an
input is missing.*
