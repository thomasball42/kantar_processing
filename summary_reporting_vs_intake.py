import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

app_strs = ["WAVE1", "WAVE2"]
colours = ["red", "blue"]
alpha = 0.3
interval_div = 4  # weeks

figs_dir = Path("..", "figs")
figs_dir.mkdir(parents=True, exist_ok=True)

rows = []

fig, axs = plt.subplots(1, 2, figsize=(8, 6))
axs = axs.flatten()

for app_str in app_strs:
    df = pd.read_csv(f"data/{app_str}/dat_th_{app_str}_with_impacts.csv")
    df.columns = df.columns.str.lower()

    df["base_week"] = df["week"] - df["week"].min()
    df["base_interval"] = df["base_week"] // interval_div

    houses = df["house"].dropna().drop_duplicates().unique()
    all_intervals = np.arange(df["base_interval"].min(), df["base_interval"].max() + 1)

    for h, house in enumerate(houses):
        print(h / len(houses), end="\r")

        house_data = df[df["house"] == house]

        for interval in all_intervals:
            interval_data = house_data[house_data["base_interval"] == interval]

            interval_cals = interval_data["kcals"].sum()
            interval_spend = interval_data["netspend"].sum()
            weekly_reports = interval_data.groupby("week")["day"].nunique().mean()

            rows.append({
                "wave": app_str,
                "house": house,
                "interval": interval,
                "interval_cals": interval_cals,
                "interval_spend": interval_spend,
                "weekly_reports": weekly_reports,
            })

print(" " * 40)
print("1.0000")

pdf = pd.DataFrame(rows)

for a, app_str in enumerate(app_strs):
    app_data = pdf[pdf["wave"] == app_str]
    app_houses = app_data["house"].dropna().drop_duplicates().unique()

    for h, house in enumerate(app_houses):
        print(h / len(app_houses), end="\r")

        house_data = app_data[app_data["house"] == house]

        mean_cals = house_data["interval_cals"].mean()
        mean_spend = house_data["interval_spend"].mean()
        mean_reports = house_data["weekly_reports"].mean()

        axs[0].scatter(
            mean_reports, mean_cals,
            color=colours[a], alpha=alpha,
            label=app_str if h == 0 else None
        )
        axs[1].scatter(
            mean_reports, mean_spend,
            color=colours[a], alpha=alpha,
            label=app_str if h == 0 else None
        )

    print("1.0000\n")

axs[0].set_xlabel("Mean weekly reports")
axs[0].set_ylabel(f"Mean calories per interval ({interval_div} weeks)")
axs[1].set_xlabel("Mean weekly reports")
axs[1].set_ylabel(f"Mean spend per interval ({interval_div} weeks)")

axs[0].legend()
axs[1].legend()

fig.tight_layout()
fig.savefig(figs_dir / f"reporting_vs_intake_{interval_div}wks.png", dpi=300)
plt.show()