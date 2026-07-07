import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from itertools import combinations
from scipy.stats import PermutationMethod

ARMS = [0, 1, 2, 3]

def aggregate(df, how="mean", experience_level="all"):

    if experience_level == "all":
        return (df.groupby(["participant", "arm"])["jaccard"].agg(how)
                .unstack("arm").reindex(columns=ARMS))
    elif experience_level == "novices":
        novices_only = df[df["experience_level"] == "Novice"]
        return (novices_only.groupby(["participant", "arm"])["jaccard"].agg(how)
                .unstack("arm").reindex(columns=ARMS))
    elif experience_level == "experts":
        experts_only = df[df["experience_level"] == "Expert"]
        return (experts_only.groupby(["participant", "arm"])["jaccard"].agg(how)
                .unstack("arm").reindex(columns=ARMS))


def friedman(wide):
    res = stats.friedmanchisquare(*[wide[a].values for a in ARMS])
    k, n = len(ARMS), wide.shape[0]
    kendall_w = res.statistic / (n * (k - 1))
    return {"chi2": res.statistic, "df": k - 1,
            "p": res.pvalue, "kendalls_w": kendall_w}


def pairwise_wilcoxon_permutation(wide, n_resamples=np.inf, rng=None):
    perm_method = PermutationMethod(n_resamples=n_resamples, rng=rng)
    recs = []
    for a, b in combinations(ARMS, 2):
        stat, p = stats.wilcoxon(
            wide[a].values, wide[b].values,
            zero_method="wilcox",
            method=perm_method
        )
        recs.append({"pair": f"{a} vs {b}", "W": stat, "p_raw": p})
    
    out = pd.DataFrame(recs)
    out["p_holm"] = multipletests(out["p_raw"], method="holm")[1]

    return out


def mannwhitney_experience(df, how="mean", arm=None):
    d = df if arm is None else df[df["arm"] == arm]
    pm = (d.groupby("participant")
            .agg(val=("jaccard", how), Experience=("experience_level", "first"))
            .reset_index())
    ex = pm.loc[pm.Experience.str.lower() == "expert", "val"].values
    nv = pm.loc[pm.Experience.str.lower() == "novice", "val"].values
    U, p = stats.mannwhitneyu(ex, nv, alternative="two-sided")
    pos = U / (len(ex) * len(nv))
    return {"n_expert": len(ex), "n_novice": len(nv), "U": U, "p": p,
            "prob_superiority": pos}


def run(df, how="mean"):
    wide = aggregate(df, how)

    fr = friedman(wide)
    print(f"Friedman:  chi2({fr['df']})={fr['chi2']:.3f}, "
          f"p={fr['p']:.4f}, Kendall's W={fr['kendalls_w']:.3f}")

    wilc = pairwise_wilcoxon_permutation(wide, group_label="overall")
    print("\nPairwise Wilcoxon signed-rank (Holm-adjusted):")
    print(wilc.to_string(index=False))

    mw = mannwhitney_experience(df, how, arm =3)
    print(f"\nMann-Whitney (experts vs novices, overall {how}): "
          f"U={mw['U']:.1f}, p={mw['p']:.4f}, "
          f"P(expert>novice)={mw['prob_superiority']:.3f}")


if __name__ == "__main__":
    records = pd.read_csv("exp_statistics/experiment_2/records.csv")
    
    run(records, how="mean")

