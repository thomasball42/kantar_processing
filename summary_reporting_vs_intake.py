import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.stats import linregress

app_strs = ["WAVE1", "WAVE2"]
colours = ["red", "blue"]
alpha = 0.3
interval_div = 4  # weeks
separate_figures = True  #

figs_dir = Path("..", "figs")
figs_dir.mkdir(parents=True, exist_ok=True)

interval_frames = []

for app_str in app_strs:
    df = pd.read_csv(f"data/{app_str}/dat_th_{app_str}_with_impacts.csv")
    df.columns = df.columns.str.lower()

    df["base_week"] = df["week"] - df["week"].min()
    df["base_interval"] = df["base_week"] // interval_div
    df["wave"] = app_str

    house_individ = (
        df.groupby("house", as_index=False)["individ"]
        .first()
    )

    df = df.drop(columns=["individ"], errors="ignore").merge(
        house_individ,
        on="house",
        how="left"
    )

    df["kcals_pc"] = df["kcals"] / df["individ"]
    df["netspend_pc"] = df["netspend"] / df["individ"]

    weekly_reports = (
        df.groupby(["wave", "house", "base_interval", "week"])["day"]
        .nunique()
        .reset_index(name="reports_in_week")
    )

    interval_weeks = (
        df[["wave", "base_interval", "week"]]
        .drop_duplicates()
    )

    houses_in_interval = (
        df[["wave", "house", "base_interval"]]
        .drop_duplicates()
    )

    all_house_weeks = houses_in_interval.merge(
        interval_weeks,
        on=["wave", "base_interval"],
        how="left"
    )

    weekly_reports_full = all_house_weeks.merge(
        weekly_reports,
        on=["wave", "house", "base_interval", "week"],
        how="left"
    )

    weekly_reports_full["reports_in_week"] = weekly_reports_full["reports_in_week"].fillna(0)

    weekly_reports_interval = (
        weekly_reports_full.groupby(["wave", "house", "base_interval"])["reports_in_week"]
        .mean()
        .reset_index(name="weekly_reports")
    )

    interval_sums = (
        df.groupby(["wave", "house", "base_interval"], as_index=False)
        .agg(
            interval_cals_pc=("kcals_pc", "sum"),
            interval_spend_pc=("netspend_pc", "sum"),
        )
    )

    interval_summary = interval_sums.merge(
        weekly_reports_interval,
        on=["wave", "house", "base_interval"],
        how="left"
    )

    interval_frames.append(interval_summary)

pdf = pd.concat(interval_frames, ignore_index=True)

house_means = (
    pdf.groupby(["wave", "house"], as_index=False)
    .agg(
        mean_cals_pc=("interval_cals_pc", "mean"),
        mean_spend_pc=("interval_spend_pc", "mean"),
        mean_reports=("weekly_reports", "mean"),
    )
)

def add_linear_fit(ax, x, y, color, label):
    x_fit = x.to_numpy(dtype=float)
    y_fit = y.to_numpy(dtype=float)

    mask = np.isfinite(x_fit) & np.isfinite(y_fit)
    x_fit = x_fit[mask]
    y_fit = y_fit[mask]

    if len(x_fit) < 2:
        return

    if np.allclose(x_fit, x_fit[0]):
        return

    res = linregress(x_fit, y_fit)

    x_line = np.linspace(x_fit.min(), x_fit.max(), 100)
    y_line = res.slope * x_line + res.intercept
    r2 = res.rvalue**2

    ax.plot(
        x_line,
        y_line,
        color=color,
        linewidth=2,
        linestyle="--",
        label=f"{label} fit ($R^2$={r2:.3f}, p={res.pvalue:.3g})"
    )

if not separate_figures:
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    for a, app_str in enumerate(app_strs):
        plot_data = house_means[house_means["wave"] == app_str]

        axs[0].scatter(
            plot_data["mean_reports"],
            plot_data["mean_cals_pc"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )
        add_linear_fit(
            axs[0],
            plot_data["mean_reports"],
            plot_data["mean_cals_pc"],
            colours[a],
            app_str,
        )

        axs[1].scatter(
            plot_data["mean_reports"],
            plot_data["mean_spend_pc"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )
        add_linear_fit(
            axs[1],
            plot_data["mean_reports"],
            plot_data["mean_spend_pc"],
            colours[a],
            app_str,
        )

    axs[0].set_xlabel("Mean weekly reports")
    axs[0].set_ylabel(f"Mean calories per person per interval ({interval_div} weeks)")
    axs[1].set_xlabel("Mean weekly reports")
    axs[1].set_ylabel(f"Mean spend per person per interval ({interval_div} weeks)")

    axs[0].legend()
    axs[1].legend()

    fig.tight_layout()
    fig.savefig(figs_dir / f"reporting_vs_intake_percap_{interval_div}wks.png", dpi=300)
    plt.show()

else:
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    fig2, ax2 = plt.subplots(figsize=(6, 6))

    for a, app_str in enumerate(app_strs):
        plot_data = house_means[house_means["wave"] == app_str]

        ax1.scatter(
            plot_data["mean_reports"],
            plot_data["mean_cals_pc"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )
        add_linear_fit(
            ax1,
            plot_data["mean_reports"],
            plot_data["mean_cals_pc"],
            colours[a],
            app_str,
        )

        ax2.scatter(
            plot_data["mean_reports"],
            plot_data["mean_spend_pc"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )
        add_linear_fit(
            ax2,
            plot_data["mean_reports"],
            plot_data["mean_spend_pc"],
            colours[a],
            app_str,
        )

    ax1.set_xlabel("Mean weekly reports")
    ax1.set_ylabel(f"Mean calories per person per interval ({interval_div} weeks)")
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(figs_dir / f"reporting_vs_kcals_percap_{interval_div}wks.png", dpi=300)

    ax2.set_xlabel("Mean weekly reports")
    ax2.set_ylabel(f"Mean spend per person per interval ({interval_div} weeks)")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(figs_dir / f"reporting_vs_spend_percap_{interval_div}wks.png", dpi=300)

    plt.show()