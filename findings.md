# Where AI Is Actually Used Across the Wage Distribution

*A short empirical note · Brendan Daly · June 2026*

## TL;DR

Joining the Anthropic Economic Index — which measures where AI is *actually* used, from real
Claude conversations mapped to occupational tasks — to BLS wages for 454 of the 756 occupations
the index covers, two patterns run in opposite directions. **Observed AI exposure rises with wages** (from 0.04 in
the lowest-paid quintile to 0.10 in the highest; Spearman ρ = 0.33, p < 10⁻¹²) and clusters in
upper-middle-wage knowledge and clerical work. A **legacy "automation risk" index falls with
wages** (0.72 → 0.14), reflecting a decade of forecasts that routine, low-wage jobs would go
first. Where AI shows up in practice is close to the mirror image of where it was predicted to
hit. Separately, across *all* classified Claude.ai conversations in the release — not within
these 454 occupations, which that file cannot be broken out by — 57% of use is augmentation
rather than automation.

## Question

For ten years the dominant labor-market story about automation was *regressive*: routine,
lower-wage jobs were "most exposed." Generative AI inverts the usual assumptions — it is best
at language, analysis, and judgment-adjacent tasks. So a simple, testable question:

> **Across the wage distribution, where is generative AI actually being used — and how does
> that compare to what earlier automation forecasts predicted?**

## Data and method

Two public sources, joined on 6-digit SOC occupation codes:

1. **Observed AI exposure** — Anthropic Economic Index (Feb 2025 release), `job_exposure.csv`.
   For each occupation, the share of its O\*NET tasks that appear in real Claude.ai usage. This
   is *revealed* use, not a survey or a forecast.
2. **Wages + a legacy automatability score** — `wage_data.csv`: BLS median annual wage by
   occupation, plus a published "probability of automation" index of the Frey-&-Osborne lineage
   (0–1) that long anchored automation-risk commentary.

I normalize wages to annual, collapse O\*NET sub-codes to their base SOC, drop occupations with
missing wages, and summarize by wage quintile, by wage decile (for the trend), and by SOC major
group. The collaboration mix (augmentation vs. automation) is taken from the index's
`automation_vs_augmentation` file, which has no occupation dimension at all — it is six global
rows over classified conversations, so that share describes the platform, not this sample. Everything is one ~120-line script; figures regenerate from
the public files (`analysis.py`).

### Coverage and selection

The join is a selection step, not a formality, and it runs against the results below.

| | Occupations |
|---|---|
| In the index (`job_exposure.csv`) | 756 |
| In the wage table (`wage_data.csv`, collapsed to 6-digit SOC) | 554 |
| **Matched, and analysed here** | **454** |
| Unmatched — no row in the legacy wage table | 302 |

The 302 unmatched occupations are **more** AI-exposed than the 454 kept ones (mean observed
exposure 0.084 versus 0.072). The single most-exposed occupation in the whole index, SOC 15-1251
at 0.745 — above Customer Service Representatives — is among them.

Be careful about what that does and does not establish. It shows the **occupation-wide mean of
the analysed sample (0.072) sits below the mean of the full index**, so as a summary of "how
exposed is work in general", this sample understates it.

It does **not** make the quintile or major-group figures lower bounds, and it does **not** show
the wage gradient is biased in either direction. The 302 are missing precisely because they have
no wage, so there is no way to say which quintiles they would have joined. If they were
concentrated at the top they would steepen the gradient; at the bottom, flatten it. The data
cannot distinguish those cases, and neither can this note.

The loss is not spread evenly. Only 4 of the index's 21 Computer & Mathematical occupations
survive the join, and 11 of 35 Management occupations are dropped. Major-group means resting on
fewer than 10 occupations are flagged as indicative in the script output and in
`results.json` (`thin_families`); Computer & Mathematical (n = 4) and Legal (n = 5) are the two
that appear in the "most-exposed groups" list below, and both should be read as suggestive
rather than estimated.

The legacy automatability score carries its own gap: `ChanceAuto` is missing for 73 of the 454
matched occupations, and the missingness is concentrated in the upper half of the wage
distribution (non-null counts by quintile: 81, 82, 83, 68, 67). The two columns in the quintile
table therefore do not share a denominator, and the mirror-image contrast is weakest exactly
where the legacy index is thinnest.

None of this is a reason to discard the comparison, but it is the reason to treat it as
illustrative rather than estimated.

## Findings

**1. Observed AI use rises with wages.** Mean exposure climbs monotonically across wage
quintiles — 0.037, 0.056, 0.066, 0.098, 0.102 — roughly a 2.8× gap between the lowest- and
highest-paid quintiles (Spearman ρ = 0.33, p < 10⁻¹²; Pearson r = 0.20). The relationship is
real but modest, and it **flattens at the very top**: the highest-wage quintile contains both
high-exposure analytic work and near-zero-exposure hands-on medicine and management, so "high
wage" is not destiny in either direction (Figure, Panel A).

**2. Where AI is used is nearly the opposite of where it was predicted to be automated.**
The legacy automatability index runs the other way — 0.72, 0.71, 0.46, 0.35, 0.14 across the
same quintiles. Plotted together (Panel B), observed use and predicted automation are close to
mirror images. The intuition that automation would hollow out the bottom does not describe how
generative AI is actually being adopted.

**3. The exposed work is cognitive and clerical — and mostly augmented, not automated.** The
most AI-exposed occupations are Customer Service Representatives (0.70), Data Entry Keyers
(0.67), Market Research Analysts (0.65), Medical Transcriptionists (0.64), and Financial
Analysts (0.57); the most-exposed major groups are Office & Administrative Support (n = 29) and
Business & Financial Operations (n = 24), with Computer & Mathematical (n = 4) and Legal (n = 5)
ranking higher still on too few occupations to carry weight. Across all classified Claude.ai
conversations in the release — a platform-wide figure, not one computed within these
occupations — **57% is augmentation** (learning, task iteration, validation) versus **43%
automation** (directive, feedback-loop), i.e. people working *with* the model more often than
handing tasks *to* it.

## Why it matters, and what I'd study next

The headline measure — *where* AI is used — is a between-occupation story. The more important
welfare question is *within* occupation: when AI enters a job, who captures the gain? The
augmentation share hints that the answer is often the worker, not just the firm. The natural
next step is to merge this exposure measure with within-occupation skill or tenure data to test
whether AI **compresses** the skill distribution — lifting novices toward the performance of
experts — or widens it. That is the question I would want to pursue with better
microdata, and it is where field evidence and these aggregate patterns can be made to speak to
each other.

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

- **The sample is selected, and the selection is not random.** 302 of the index's 756
  occupations have no row in the legacy wage table and are dropped. They are on average more
  AI-exposed than the ones kept, so this sample understates exposure *overall*. Because they
  have no wage, their effect on the wage gradient is unknown and not assumed here. See
  *Coverage and selection* above.
- **Exposure ≠ impact.** Task presence in Claude usage measures *where* AI is applied, not
  productivity, employment, or wage effects.
- **Modest correlation, heterogeneous top.** The wage-exposure gradient is real but not strong,
  and the highest quintile is internally mixed; I avoid over-reading a clean monotonic story.
- **Two non-identical instruments.** Observed exposure (revealed Claude usage) and the legacy
  automatability score (an expert-prediction index) are different constructs measured at
  different times; the contrast is illustrative, not a controlled comparison.
- **Snapshot.** The index is an early (Feb 2025) release and AI adoption is moving fast; later
  releases would update the levels, likely upward.

## Sources

- Anthropic Economic Index, *Which Economic Tasks Are Performed with AI?* (Feb 2025 release), CC-BY. <https://huggingface.co/datasets/Anthropic/EconomicIndex>
- Brynjolfsson, Li & Raymond, *Generative AI at Work*, QJE 140(2), 2025 (NBER w31161).
- BLS Occupational Employment and Wage Statistics (median wages) and a published Frey-&-Osborne-lineage automatability index, via the index's `wage_data.csv`.
