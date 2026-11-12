# Observed AI Exposure Across the Wage Distribution

*A short empirical note · Brendan Daly · June 2026; correction prepared November 11, 2026*

## Finding

Across 672 occupations that match a legacy wage table, Anthropic's observed-exposure
measure is modestly positively associated with wages (Spearman ρ = 0.288,
p = 2.55 × 10⁻¹⁴; Pearson r = 0.169). Mean exposure is 0.038 in the lowest wage quintile
and 0.105 in the highest, with a small dip from Q2 to Q3. Legacy predicted automatability
falls from 0.745 to 0.177. This is a descriptive contrast between different measures and
vintages, rather than evidence that an earlier forecast has been falsified.

The inputs and resulting numbers were corrected after verification found a truncated wage
file and two unexplained exposure edits. [CORRECTIONS.md](CORRECTIONS.md) records the
previous baseline and all headline changes.

## Question

How does observed occupational AI exposure vary across the legacy wage distribution,
and how does that descriptive pattern compare with an older automatability score?

## Data and method

Two occupational inputs are joined on the six-digit part of their SOC codes:

1. **Observed exposure:** `labor_market_impacts/job_exposure.csv`, associated with
   [Anthropic's March 5, 2026 paper](https://www.anthropic.com/research/labor-market-impacts).
   It combines theoretical task feasibility and work-related observed usage, weights
   automation more heavily than augmentation, and aggregates using task-time weights.
   It includes Claude.ai and API evidence, and is not a simple task-presence or usage share.
2. **Legacy wages and automatability:** the February 2025 release's `wage_data.csv`,
   itself byte-identical to an O*NET scrape committed in January 2020. Checked wage values
   match May 2018 BLS medians; the original scrape does not establish one uniform wage
   reference year. `ChanceAuto` was scraped from willrobotstakemyjob.com and is a legacy
   predicted-automatability score, rather than a current generative-AI estimate.

All three CSVs are frozen at an immutable Anthropic dataset revision, with checksums,
row counts and retrieval verification in [data/input_manifest.json](data/input_manifest.json).
Their original retrieval date into this repository is unknown; November 11, 2026 is the
verification and repair date. [data/SOURCES.md](data/SOURCES.md) traces their provenance.

The analysis preserves the original cleaning choices: salary values below $1,000 are
assumed hourly and multiplied by 2,080; negative automatability values become missing;
O*NET subcodes collapse to six-digit SOC by median; missing/nonpositive wages are dropped.
These are explicit conventions, not a modern SOC crosswalk or a new wage-data collection.
No inflation adjustment or employment weighting is applied: each occupation counts once.

A **third input**, the February 2025 `automation_vs_augmentation.csv`, supplies only a
separate platform-wide collaboration statistic. It has no occupation dimension and cannot
be joined to the 672 occupations or used to infer their interaction mix.

## Coverage and selection

| Input / join step | Occupations |
|---|---:|
| Exposure index | 756 |
| Complete wage table, collapsed to six-digit SOC | 821 |
| Matched with valid wages | 672 |
| Exposure occupations unmatched | 84 |

The unmatched mean exposure is 0.1325, compared with 0.0700 in the matched sample. Thus the
matched occupation-wide mean sits below the full exposure index mean. This does not make
any quintile or major-group figure a lower bound, or identify the direction of bias in the
wage gradient: the unmatched occupations have no wage in this table.

The most-exposed occupation overall, Computer Programmers (SOC 15-1251, exposure 0.7451),
remains unmatched. Only 5 of the exposure index's 21 Computer and Mathematical occupations
match; Computer and Mathematical (n = 5) and Legal (n = 7) means are indicative. All groups
with fewer than 10 occupations are flagged in console output and `results.json`.

The legacy automatability score is missing for 89 of the matched occupations, with
nonmissing counts 123, 121, 124, 109 and 106 across the five wage quintiles. Its column
therefore has a different denominator from observed exposure. Neither the legacy SOC
codes nor the two score definitions are treated as directly interchangeable instruments.

## Findings

**1. The positive relationship is modest and not monotonic across every quintile.**
Mean exposure is 0.038, 0.057, 0.056, 0.095 and 0.105 across wage quintiles. The highest
quintile is about 2.8 times the lowest, but occupation-level variation is substantial.
Correlation and quintile averages describe this matched sample; they are not wage effects.

**2. The legacy automatability pattern runs in the other direction.**
Its quintile means are 0.745, 0.704, 0.566, 0.395 and 0.177. The chart contrasts these
patterns while retaining their distinct constructs, vintages and missing-value denominators.
It does not test whether either measure predicted an actual labor-market outcome.

**3. Exposure is concentrated in particular cognitive, clerical and sales roles.**
The five most-exposed matched occupations are Customer Service Representatives (0.7011),
Data Entry Keyers (0.6707), Market Research Analysts (0.6483), Medical Transcriptionists
(0.6365), and nontechnical Wholesale and Manufacturing Sales Representatives (0.6279).
Among major groups with at least ten matched occupations, Sales and Related (n = 20) and
Office and Administrative Support (n = 50) have the highest means. The higher Computer
and Mathematical (n = 5) and Legal (n = 7) means rest on thin samples.

**4. The February 2025 collaboration mix is separate context.**
In that release, augmentation accounts for 57.4% and automation for 42.6% of the five named
interaction types. Those types cover approximately 81.3% of conversations, with `none` and
unrepresented categories outside the denominator. This statistic has no occupational or
wage breakdown and is not contemporaneous with the exposure measure.

## Why it matters, and what I would study next

The exposure–wage relationship is a between-occupation description. It does not answer
who captures productivity gains within an occupation, or whether workers' wages change.
The collaboration mix likewise does not identify who benefits. A next study could examine
modern wage/SOC coverage and within-occupation skill or tenure data; that work would need
a new versioned analysis and a research design suited to those questions.

## A practitioner's note

I have watched this from inside one of the most-exposed occupations in the data. Leading an
AI deployment to 2,500+ contact-center agents, I saw the within-occupation version of these
patterns directly: new and bottom-quartile agents closed the performance gap fastest, because
the system delivered, in real time, guidance distilled from top performers; tenured experts
gained least; onboarding accelerated and attrition fell. That mirrors the published
contact-center evidence (Brynjolfsson, Li & Raymond, 2025: +14% on average, +34% for novices),
and it is the empirical instinct behind this note — that the interesting action in AI's
economic impact is distributional, and measurable.

## Caveats

- **Selected sample:** 84 exposure occupations lack matching valid wages. Their effect on
  the wage gradient is unknown; no bias direction is assumed.
- **Exposure is a composite, not an outcome:** theoretical capability and usage evidence
  enter its construction. It does not estimate productivity, employment or wage impacts.
- **Legacy wages and codes:** the wage scrape predates 2020, checked records match May 2018,
  and its uniform vintage is unverified. The six-digit join is not a SOC-version crosswalk.
- **Distinct scores and denominators:** the observed-exposure and legacy automatability
  columns are different constructs, measured at different times, with 89 legacy scores missing.
- **Limited generalization:** Claude traffic is not all AI use, occupations are unweighted,
  and thin group samples and within-quintile variation limit broad claims.
- **Mixed releases:** the March 2026 exposure publication and February 2025 collaboration
  mix must not be interpreted as one contemporaneous occupational dataset.

## Sources

- Anthropic, *Labor market impacts of AI: A new measure and early evidence* (March 5, 2026),
  linked above, and the immutable files listed in `data/input_manifest.json`.
- Anthropic, *Which Economic Tasks Are Performed with AI?* (February 2025), for the separate
  collaboration mix and distributed legacy wage table.
- The upstream O*NET scrape and BLS May 2018 wage spot checks are linked in `data/SOURCES.md`.
- Brynjolfsson, Li & Raymond, *Generative AI at Work*, QJE 140(2), 2025 (NBER w31161),
  cited as background for the practitioner's note, not as an input to this analysis.
