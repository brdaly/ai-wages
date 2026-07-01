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
- Augmentation = learning + task iteration + validation; Automation = directive + feedback loop. Shares computed over classified interactions (excludes "none" / not-classified).

## 3. `wage_data.csv` — wages + legacy automatability
- **Source:** Anthropic Economic Index, `release_2025_02_10/wage_data.csv` (bundles BLS median wages and a published Frey-&-Osborne-lineage automation-probability index).
- **URL:** https://huggingface.co/datasets/Anthropic/EconomicIndex/raw/main/release_2025_02_10/wage_data.csv
- **Fields used:** `SOCcode` (O\*NET-SOC), `JobFamily` (SOC major group), `MedianSalary`, `ChanceAuto` (0–100; −1 = missing).
- **Cleaning:** `MedianSalary` < 1000 treated as hourly → ×2080; `ChanceAuto` of −1 set to missing then scaled to 0–1; O\*NET sub-codes collapsed to base 6-digit SOC by median.

## Underlying public references
- BLS Occupational Employment and Wage Statistics (OEWS), May 2024 — https://www.bls.gov/oes/
- O\*NET task statements & SOC structure — U.S. Department of Labor (public domain)
- Brynjolfsson, Li & Raymond, *Generative AI at Work*, NBER w31161 / QJE 140(2), 2025

*Reproducibility note: the three CSVs were retrieved from the URLs above. `wage_data.csv` is stored
with its original header row (the analysis script also handles a raw fetch cache automatically).*
