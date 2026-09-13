"""
Where is AI actually used across the wage distribution?
=======================================================
Joins Anthropic Economic Index *observed* AI exposure (share of an occupation's
work that shows up in real Claude usage) to BLS occupational wages, and contrasts
it with a legacy *predicted* automatability score.

Public data, fully reproducible. Sources in data/SOURCES.md.

Author: Brendan Daly
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

DATA = "data"
FIG = "figures"

# The quintile table gained a column; keep it printable on one line.
pd.set_option("display.width", 160, "display.max_columns", None)

# ----------------------------------------------------------------------
# 1. Load Anthropic Economic Index "observed AI exposure" by occupation
#    (labor_market_impacts/job_exposure.csv: occ_code = 6-digit SOC)
# ----------------------------------------------------------------------
exp = pd.read_csv(f"{DATA}/job_exposure.csv")
exp["soc6"] = exp["occ_code"].str.strip()
exp = exp[["soc6", "observed_exposure"]]

# ----------------------------------------------------------------------
# 2. Load wage + legacy automatability table (release_2025_02_10/wage_data.csv)
# ----------------------------------------------------------------------
def load_wage_data():
    local = f"{DATA}/wage_data.csv"
    try:
        return pd.read_csv(local)
    except FileNotFoundError as missing:
        raise SystemExit(
            f"{local} is missing. Re-download it from the URL recorded in "
            f"{DATA}/SOURCES.md, which pins the release this analysis was run against."
        ) from missing

wd = load_wage_data()
wd["soc6"] = wd["SOCcode"].str.split(".").str[0]

# MedianSalary mixes annual ($) and a few hourly rows (< $1000). Normalise to annual.
wd["wage"] = wd["MedianSalary"].where(wd["MedianSalary"] >= 1000, wd["MedianSalary"] * 2080)
# Legacy predicted automatability (0-100; -1 = missing)
wd["chance_auto"] = wd["ChanceAuto"].where(wd["ChanceAuto"] >= 0, np.nan) / 100.0

wd_soc = (wd.groupby("soc6")
            .agg(wage=("wage", "median"),
                 chance_auto=("chance_auto", "median"),
                 family=("JobFamily", "first"))
            .reset_index())

# ----------------------------------------------------------------------
# 3. Join observed exposure <-> wages
# ----------------------------------------------------------------------
df = exp.merge(wd_soc, on="soc6", how="inner").dropna(subset=["wage"])
df = df[df["wage"] > 0]
n = len(df)

# The wage table is a legacy file and does not cover every occupation the index
# reports, so the inner join is a selection step, not a formality. Measure it:
# the unmatched set is more AI-exposed than the matched set, which makes every
# level reported below a lower bound and the major-group means conditional on
# which occupations happened to survive.
unmatched = exp[~exp["soc6"].isin(set(df["soc6"]))]
coverage = {
    "exposure_occupations": int(exp["soc6"].nunique()),
    "wage_occupations": int(wd_soc["soc6"].nunique()),
    "matched": int(n),
    "unmatched": int(len(unmatched)),
    "mean_exposure_matched": round(float(df["observed_exposure"].mean()), 4),
    "mean_exposure_unmatched": round(float(unmatched["observed_exposure"].mean()), 4),
    "most_exposed_unmatched_soc": str(
        unmatched.sort_values("observed_exposure", ascending=False)["soc6"].iloc[0]
    ),
    "most_exposed_unmatched_value": round(
        float(unmatched["observed_exposure"].max()), 4
    ),
}

# ----------------------------------------------------------------------
# 4. Headline relationships
# ----------------------------------------------------------------------
logw = np.log10(df["wage"])
r_lin, p_lin = stats.pearsonr(df["wage"], df["observed_exposure"])
rho, p_rho = stats.spearmanr(df["wage"], df["observed_exposure"])

# Wage quintiles
df["wage_q"] = pd.qcut(df["wage"], 5, labels=["Q1 (lowest pay)", "Q2", "Q3", "Q4", "Q5 (highest pay)"])
by_q = df.groupby("wage_q", observed=True).agg(
    n=("soc6", "size"),
    median_wage=("wage", "median"),
    mean_AI_exposure=("observed_exposure", "mean"),
    mean_predicted_automatability=("chance_auto", "mean"),
    # chance_auto is missing for 73 of the 454 matched occupations, so this
    # column does not share the denominator of the one beside it.
    n_predicted_automatability=("chance_auto", "count"),
)

# Wage deciles (for the trend line / inverted-U test)
df["wage_d"] = pd.qcut(df["wage"], 10, labels=False)
dec = df.groupby("wage_d").agg(mid_wage=("wage", "median"),
                               exposure=("observed_exposure", "mean")).reset_index()

# By SOC major group
fam = (df.groupby("family")
         .agg(n=("soc6", "size"),
              median_wage=("wage", "median"),
              mean_exposure=("observed_exposure", "mean"))
         .sort_values("mean_exposure", ascending=False))

top = df.sort_values("observed_exposure", ascending=False).head(12)

# ----------------------------------------------------------------------
# 5. Augmentation vs automation (collaboration mix), AEI 2025-02-10
# ----------------------------------------------------------------------
collab = pd.read_csv(f"{DATA}/automation_vs_augmentation.csv").set_index("interaction_type")["pct"]
automation = collab["directive"] + collab["feedback loop"]
augmentation = collab["learning"] + collab["task iteration"] + collab["validation"]
classified = automation + augmentation
aug_share, auto_share = augmentation / classified, automation / classified

# ----------------------------------------------------------------------
# 6. Report
# ----------------------------------------------------------------------
print(f"Occupations matched (observed exposure x wage): {n}")
print(f"  of {coverage['exposure_occupations']} in the index; "
      f"{coverage['unmatched']} unmatched (no row in the wage table)")
print(f"  mean exposure: matched {coverage['mean_exposure_matched']:.4f}, "
      f"unmatched {coverage['mean_exposure_unmatched']:.4f} "
      f"- the dropped occupations are the more exposed set")
print(f"  most-exposed occupation overall, SOC {coverage['most_exposed_unmatched_soc']} "
      f"at {coverage['most_exposed_unmatched_value']:.4f}, is unmatched")
print(f"Pearson  r(wage, exposure)  = {r_lin:+.3f}  (p={p_lin:.1e})")
print(f"Spearman rho(wage, exposure)= {rho:+.3f}  (p={p_rho:.1e})")
print(f"Augmentation {aug_share:.1%} vs automation {auto_share:.1%} of classified usage\n")
print("By wage quintile:\n", by_q.round(3), "\n")
MIN_FAMILY_N = 10
thin = fam[fam["n"] < MIN_FAMILY_N]
print("Top exposed major groups:\n", fam.head(8).round(3), "\n")
if len(thin):
    print(f"Major groups below n={MIN_FAMILY_N}, read as indicative only:",
          ", ".join(f"{name} (n={int(row.n)})" for name, row in thin.iterrows()), "\n")
print("Most-exposed occupations:\n",
      top.merge(wd[['soc6','JobName']].drop_duplicates('soc6'), on='soc6')[['JobName','wage','observed_exposure']]
         .to_string(index=False))

results = {
    "n_occupations": int(n),
    "coverage": coverage,
    "min_family_n": MIN_FAMILY_N,
    "thin_families": {str(name): int(row.n) for name, row in thin.iterrows()},
    "pearson_wage_exposure": round(r_lin, 3),
    "spearman_wage_exposure": round(rho, 3),
    "augmentation_share": round(aug_share, 3),
    "automation_share": round(auto_share, 3),
    "by_wage_quintile": json.loads(by_q.round(4).reset_index().to_json(orient="records")),
    "by_major_group": json.loads(
        fam.round(4).reset_index().to_json(orient="records")
    ),
    "peak_decile_exposure": float(dec["exposure"].max()),
    "peak_decile_index": int(dec["exposure"].idxmax()),
}
json.dump(results, open("results.json", "w"), indent=2)

# ----------------------------------------------------------------------
# 7. Figure
# ----------------------------------------------------------------------
NAVY, ORANGE, GREY = "#1f3a5f", "#d97706", "#9aa6b2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))

# Panel A: occupation scatter + decile trend
ax[0].scatter(df["wage"], df["observed_exposure"], s=14, c=GREY, alpha=0.55, edgecolor="none")
ax[0].plot(dec["mid_wage"], dec["exposure"], "-o", color=NAVY, lw=2.4, ms=6, label="Mean exposure (wage decile)")
ax[0].set_xscale("log")
ax[0].set_xticks([30000, 50000, 100000, 200000])
ax[0].get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax[0].set_xlabel("Median annual wage (BLS, log scale)")
ax[0].set_ylabel("Observed AI exposure  (share of work seen in Claude usage)")
ax[0].set_title("A.  AI use is concentrated in upper-middle-wage knowledge work", fontsize=11.5, color=NAVY, loc="left")
ax[0].legend(frameon=False, fontsize=9)

# Panel B: observed exposure vs predicted automatability by wage quintile
qlabels = list(by_q.index)
x = np.arange(len(qlabels)); w = 0.38
ax[1].bar(x - w/2, by_q["mean_AI_exposure"], w, color=NAVY, label="Observed AI exposure (Anthropic)")
ax[1].bar(x + w/2, by_q["mean_predicted_automatability"], w, color=ORANGE, label="Predicted automatability (legacy index)")
ax[1].set_xticks(x); ax[1].set_xticklabels(["Q1\nlowest", "Q2", "Q3", "Q4", "Q5\nhighest"])
ax[1].set_xlabel("Occupation wage quintile")
ax[1].set_ylabel("Mean score")
ax[1].set_title("B.  Where AI is used ≠ what was predicted to be automated", fontsize=11.5, color=NAVY, loc="left")
ax[1].legend(frameon=False, fontsize=9)

fig.suptitle("Where AI is actually used across the wage distribution",
             fontsize=14, fontweight="bold", color=NAVY, x=0.012, ha="left")
fig.text(0.012, 0.005,
         "Source: Anthropic Economic Index (Claude.ai usage, O*NET tasks) joined to BLS wages. "
         f"n={n} occupations. Observed exposure vs. a legacy predicted-automatability index.",
         fontsize=8, color="#666")
fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.savefig(f"{FIG}/ai_exposure_wage.png", dpi=150, bbox_inches="tight")
print("\nSaved figures/ai_exposure_wage.png and results.json")
