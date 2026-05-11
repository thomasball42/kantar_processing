import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

app_str = "WAVE1"

app_strs = ["WAVE1", "WAVE2"]

figs_dir = Path("..", "figs", app_str)

fig, axs = plt.subplots(2,1, 
                       figsize=(5, 7))

for a, app_str in enumerate(app_strs):
    if not figs_dir.exists():
        figs_dir.mkdir(parents=True)

    df = pd.read_csv(f"data/{app_str}/dat_th_{app_str}_with_impacts.csv")

    df.columns = df.columns.str.lower()

    # hh_data = pd.read_csv(f"data/{app_str}/raw/pan_th_new.csv")
    hh_data = pd.read_csv("data/pan_th_ALL.csv")

    hh_sizes = hh_data[['house', 'size']].drop_duplicates()

    cols = ["netspend", "kcals"]

    # all_houses = hh_sizes["house"].drop_duplicates().sort_values()
    all_houses = df["house"].dropna().drop_duplicates().unique()

    all_weeks = np.sort(df["week"].dropna().unique())
    all_days = np.arange(1, 8)

    sums = df.groupby(["house", "week"])[cols].sum().reset_index()

    weeks_reported = sums.groupby("house")["week"].nunique()
    weeks_reported = weeks_reported[weeks_reported>0]
    weeks_reported = weeks_reported.reindex(all_houses, fill_value=0)

    axs[0].hist(weeks_reported, 
                bins=weeks_reported.max()+1, 
                edgecolor=None,
                alpha = 0.4,
                label=app_str)

    axs[0].set_xlabel("Number of weeks reported")
    axs[0].set_ylabel("Number of houses")
    axs[0].legend()

    sums = df.groupby(["house", "week", "day"])[cols].sum().reset_index()

    # days_per_week = sums.groupby(["house", "week"])["day"].nunique().reset_index(name="days_reported")
    # mean_days_per_week = days_per_week.groupby("house")["days_reported"].mean()
    # mean_days_per_week = mean_days_per_week.reindex(all_houses, fill_value=0)

    # axs[1].hist(mean_days_per_week, 
    #             bins=all_days, 
    #             edgecolor=None,
    #             facecolor="green",
    #             alpha=0.4,
    #             label = app_str)
    # axs[1].set_xlabel("Mean days reported per week")
    # axs[1].set_ylabel("Number of houses")
    # axs[1].legend()

    reports_per_week = sums.groupby(["house", "week"])["day"].nunique()

    axs[1].hist(
        reports_per_week,
        bins=np.arange(0, 9) - 0.5,
        edgecolor=None,
        alpha=0.4,
        label=app_str
    )

    axs[1].set_xlabel("Number of days reported in a week")
    axs[1].set_ylabel("Number of house-weeks")
    axs[1].legend()

    
fig.tight_layout()
fig.savefig(figs_dir / "reporting_frequency_hist.png")
plt.show()
