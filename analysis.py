"""
Where is AI actually used across the wage distribution?
=======================================================
Joins Anthropic Economic Index *observed* AI exposure (share of an occupation's
work that shows up in real Claude usage) to BLS occupational wages, and contrasts
it with a legacy *predicted* automatability score.

Public data, fully reproducible. Sources in data/SOURCES.md.

Author: Brendan Daly
"""
import glob, re, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

DATA = "data"
FIG = "figures"

# ----------------------------------------------------------------------
# 1. Load Anthropic Economic Index "observed AI exposure" by occupation
#    (labor_market_impacts/job_exposure.csv: occ_code = 6-digit SOC)
# ----------------------------------------------------------------------
exp = pd.read_csv(f"{DATA}/job_exposure.csv")
exp["soc6"] = exp["occ_code"].str.strip()
exp = exp[["soc6", "observed_exposure"]]

# ----------------------------------------------------------------------
# 2. Load wage + legacy automatability table (release_2025_02_10/wage_data.csv).
#    The raw web_fetch cache prepends 4 header lines; find the real header.
# ----------------------------------------------------------------------
def load_wage_data():
    # local copy if present, else the fetch cache
    local = f"{DATA}/wage_data.csv"
    try:
        return pd.read_csv(local)
    except Exception:
        pass
    cands = glob.glob("/sessions/**/tool-results/*.txt", recursive=True)
    path = next(p for p in cands if "SOCcode,JobName" in open(p, errors="ignore").read())
    lines = open(path, errors="ignore").read().splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("SOCcode,"))
    with open(local, "w") as f:
        f.write("\n".join(lines[start:]))
    return pd.read_csv(local)

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
collab = {"directive": 22.56, "feedback loop": 12.04, "learning": 18.92,
          "task iteration": 25.48, "validation": 2.31, "none": 2.90}
automation = collab["directive"] + collab["feedback loop"]
augmentation = collab["learning"] + collab["task iteration"] + collab["validation"]
classified = automation + augmentation
aug_share, auto_share = augmentation / classified, automation / classified

# ----------------------------------------------------------------------
# 6. Report
# ----------------------------------------------------------------------
print(f"Occupations matched (observed exposure x wage): {n}")
print(f"Pearson  r(wage, exposure)  = {r_lin:+.3f}  (p={p_lin:.1e})")
print(f"Spearman rho(wage, exposure)= {rho:+.3f}  (p={p_rho:.1e})")
print(f"Augmentation {aug_share:.1%} vs automation {auto_share:.1%} of classified usage\n")
print("By wage quintile:\n", by_q.round(3), "\n")
print("Top exposed major groups:\n", fam.head(8).round(3), "\n")
print("Most-exposed occupations:\n",
      top.merge(wd[['soc6','JobName']].drop_duplicates('soc6'), on='soc6')[['JobName','wage','observed_exposure']]
         .to_string(index=False))

results = {
    "n_occupations": int(n),
    "pearson_wage_exposure": round(r_lin, 3),
    "spearman_wage_exposure": round(rho, 3),
    "augmentation_share": round(aug_share, 3),
    "automation_share": round(auto_share, 3),
    "by_wage_quintile": json.loads(by_q.round(4).reset_index().to_json(orient="records")),
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
