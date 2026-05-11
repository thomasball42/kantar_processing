import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

app_strs = ["WAVE1", "WAVE2"]
colours = ["red", "blue"]
alpha = 0.3
identifiers = [["house", "week"]]

fig, axs = plt.subplots(2, 2, figsize=(10, 7), sharex="col", sharey="col")
axs = axs.flatten()

figs_dir = Path("..", "figs")
figs_dir.mkdir(parents=True, exist_ok=True)

for a, app_str in enumerate(app_strs):
    df = pd.read_csv(f"data/{app_str}/dat_th_{app_str}_with_impacts.csv")
    df.columns = df.columns.str.lower()

    if app_str == "WAVE1":
        hh_data = pd.read_csv(f"data/{app_str}/raw/pan_th_new.csv")
    else:
        hh_data = pd.read_csv(f"data/{app_str}/raw/pan_th.csv")

    hh_sizes = hh_data[["house", "size"]].drop_duplicates()
    cols = ["netspend", "kcals"]

    all_houses = df["house"].dropna().drop_duplicates().unique()
    all_weeks = np.sort(df["week"].dropna().unique())
    all_days = np.arange(1, 8)

    for identifier in identifiers:
        if "day" in identifier:
            plustr = "daily"
            sinstr = "day"
        else:
            plustr = "weekly"
            sinstr = "week"

        sums = df.groupby(identifier)[cols].sum().reset_index()

        levels = []
        if "house" in identifier:
            levels.append(all_houses)
        if "week" in identifier:
            levels.append(all_weeks)
        if "day" in identifier:
            levels.append(all_days)

        full_panel = pd.MultiIndex.from_product(levels, names=identifier).to_frame(index=False)

        sums_full = full_panel.merge(sums, on=identifier, how="left")
        sums_full[cols] = sums_full[cols].fillna(0)

        sums_full = sums_full.merge(hh_sizes, on="house", how="left", validate="many_to_one")
        sums_full["netspend_per_capita"] = sums_full["netspend"] / sums_full["size"]
        sums_full["kcals_per_capita"] = sums_full["kcals"] / sums_full["size"]

        avg_by_house = sums_full.groupby("house")[["kcals_per_capita", "netspend_per_capita"]].mean()

        sums = sums.merge(hh_sizes, on="house", how="left", validate="many_to_one")
        sums["netspend_per_capita"] = sums["netspend"] / sums["size"]
        sums["kcals_per_capita"] = sums["kcals"] / sums["size"]

        rep_kcals = sums.groupby("house")["kcals_per_capita"].mean()
        rep_spend = sums.groupby("house")["netspend_per_capita"].mean()

        avg_kcals = avg_by_house["kcals_per_capita"]
        avg_spend = avg_by_house["netspend_per_capita"]

        kcals_cutoff = max(avg_kcals.quantile(0.99), rep_kcals.quantile(0.99))
        spend_cutoff = max(avg_spend.quantile(0.99), rep_spend.quantile(0.99))

        avg_kcals_trunc = avg_kcals[avg_kcals <= kcals_cutoff]
        rep_kcals_trunc = rep_kcals[rep_kcals <= kcals_cutoff]
        avg_spend_trunc = avg_spend[avg_spend <= spend_cutoff]
        rep_spend_trunc = rep_spend[rep_spend <= spend_cutoff]

        kcals_bins = np.linspace(0, kcals_cutoff, 41)
        spend_bins = np.linspace(0, spend_cutoff, 41)

        axs[0].hist(avg_kcals_trunc, bins=kcals_bins, alpha=alpha, facecolor=colours[a], label=app_str)
        axs[0].set_xlabel(f"Mean {plustr} kcals per capita (inc. unreported {sinstr}s as 0)")
        axs[0].set_ylabel("Frequency")

        axs[1].hist(avg_spend_trunc, bins=spend_bins, alpha=alpha, facecolor=colours[a], label=app_str)
        axs[1].set_xlabel(f"Mean {plustr} net spend (£) per capita (inc. unreported {sinstr}s as 0)")

        axs[2].hist(rep_kcals_trunc, bins=kcals_bins, alpha=alpha, facecolor=colours[a], label=app_str)
        axs[2].set_xlabel(f"{plustr} kcals per capita (reported {sinstr}s only)")
        axs[2].set_ylabel("Frequency")
        axs[2].set_xlim(0, kcals_cutoff)

        axs[3].hist(rep_spend_trunc, bins=spend_bins, alpha=alpha, facecolor=colours[a], label=app_str)
        axs[3].set_xlabel(f"{plustr} net spend (£) per capita (reported {sinstr}s only)")
        axs[3].set_xlim(0, spend_cutoff)

for ax in axs:
    ax.legend()

fig.tight_layout()
fig.savefig(figs_dir / f"{plustr}_per_cap_stats_.png")
plt.show()