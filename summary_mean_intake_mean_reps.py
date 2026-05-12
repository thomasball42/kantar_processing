import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.stats import linregress

app_strs = ["WAVE1", "WAVE2"]
colours = ["red", "blue"]
alpha = 0.3
interval_div = 4  # weeks
SEPARATE_FIGURES = True
LIN_FITS = True
INC_ZEROES = True

figs_dir = Path("..", "figs")
figs_dir.mkdir(parents=True, exist_ok=True)

interval_frames = []


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

    interval_reports = (
        df.groupby(["wave", "house", "base_interval"])["day"]
        .nunique()
        .reset_index(name="reports_in_interval")
    )

    if INC_ZEROES:
        interval_summary = (
            df.groupby(["wave", "house", "base_interval"], as_index=False)
            .agg(
                interval_cals_pc_total=("kcals_pc", "sum"),
                interval_spend_pc_total=("netspend_pc", "sum"),
            )
            .merge(
                interval_reports,
                on=["wave", "house", "base_interval"],
                how="left"
            )
        )

        interval_summary["interval_cals_pppd"] = (
            interval_summary["interval_cals_pc_total"] / (interval_div * 7)
        )
        interval_summary["interval_spend_pppd"] = (
            interval_summary["interval_spend_pc_total"] / (interval_div * 7)
        )
    else:
        interval_summary = (
            df.groupby(["wave", "house", "base_interval"], as_index=False)
            .agg(
                interval_cals_pc_total=("kcals_pc", "sum"),
                interval_spend_pc_total=("netspend_pc", "sum"),
                interval_days=("day", "nunique"),
            )
            .merge(
                interval_reports,
                on=["wave", "house", "base_interval"],
                how="left"
            )
        )

        interval_summary["interval_cals_pppd"] = (
            interval_summary["interval_cals_pc_total"] / interval_summary["interval_days"]
        )
        interval_summary["interval_spend_pppd"] = (
            interval_summary["interval_spend_pc_total"] / interval_summary["interval_days"]
        )

    interval_frames.append(interval_summary)

pdf = pd.concat(interval_frames, ignore_index=True)

house_means = (
    pdf.groupby(["wave", "house"], as_index=False)
    .agg(
        mean_cals_pppd=("interval_cals_pppd", "mean"),
        mean_spend_pppd=("interval_spend_pppd", "mean"),
        mean_reports=("reports_in_interval", "mean"),
    )
)

if not SEPARATE_FIGURES:
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    for a, app_str in enumerate(app_strs):
        plot_data = house_means[house_means["wave"] == app_str]

        axs[0].scatter(
            plot_data["mean_reports"],
            plot_data["mean_cals_pppd"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )
        if LIN_FITS:
            add_linear_fit(
                axs[0],
                plot_data["mean_reports"],
                plot_data["mean_cals_pppd"],
                colours[a],
                app_str,
            )

        axs[1].scatter(
            plot_data["mean_reports"],
            plot_data["mean_spend_pppd"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )
        if LIN_FITS:
            add_linear_fit(
                axs[1],
                plot_data["mean_reports"],
                plot_data["mean_spend_pppd"],
                colours[a],
                app_str,
            )

    axs[0].set_xlabel(f"Mean reports per {interval_div}-week interval")
    axs[0].set_ylabel(f"Mean calories per person per day ({interval_div}-week interval average)")
    axs[1].set_xlabel(f"Mean reports per {interval_div}-week interval")
    axs[1].set_ylabel(f"Mean spend per person per day ({interval_div}-week interval average)")

    axs[0].legend()
    axs[1].legend()

    fig.tight_layout()
    fig.savefig(figs_dir / f"reporting_vs_intake_percap_perday_{interval_div}wks.png", dpi=300)
    plt.show()

else:
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    fig2, ax2 = plt.subplots(figsize=(6, 6))

    for a, app_str in enumerate(app_strs):
        plot_data = house_means[house_means["wave"] == app_str]

        ax1.scatter(
            plot_data["mean_reports"],
            plot_data["mean_cals_pppd"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )

        ax2.scatter(
            plot_data["mean_reports"],
            plot_data["mean_spend_pppd"],
            color=colours[a],
            alpha=alpha,
            label=app_str,
        )

        if LIN_FITS:
            add_linear_fit(
                ax1,
                plot_data["mean_reports"],
                plot_data["mean_cals_pppd"],
                colours[a],
                app_str,
            )
            add_linear_fit(
                ax2,
                plot_data["mean_reports"],
                plot_data["mean_spend_pppd"],
                colours[a],
                app_str,
            )

    ax1.set_xlabel(f"Mean reports per {interval_div}-week interval")
    ax1.set_ylabel(f"Mean kcal per person per day ({interval_div}-week interval average)")
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(figs_dir / f"reporting_vs_kcals_percap_perday_{interval_div}wks.png", dpi=300)

    ax2.set_xlabel(f"Mean reports per {interval_div}-week interval")
    ax2.set_ylabel(f"Mean spend per person per day ({interval_div}-week interval average)")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(figs_dir / f"reporting_vs_spend_percap_perday_{interval_div}wks.png", dpi=300)

    plt.show()