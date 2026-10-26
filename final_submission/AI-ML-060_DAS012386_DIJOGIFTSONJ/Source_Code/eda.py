"""
Exploratory Data Analysis (EDA) module for AI-ML-060:
Intelligent Air Quality Prediction and Environmental Monitoring System
"""

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger

# Styling parameters
PRIMARY_COLOR = "#0f766e"    # Teal
SECONDARY_COLOR = "#1b4934"  # Dark Forest Green
ACCENT_COLOR = "#d97706"     # Amber
NAVY_COLOR = "#1e293b"       # Dark Navy
LIGHT_BG = "#f8fafc"         # Off-white

sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300


def plot_target_bar(y, save_path=None):
    """Figure 1: Target distribution bar chart."""
    fig, ax = plt.subplots(figsize=(7, 5))
    counts = y.value_counts().sort_index()
    labels = ["Low CO (<= 4.0 mg/m³)", "High CO (> 4.0 mg/m³)"]
    colors = [PRIMARY_COLOR, "#dc2626"]
    
    bars = ax.bar(labels, counts.values, color=colors, width=0.45, edgecolor=NAVY_COLOR, linewidth=1.2)
    for bar in bars:
        h = bar.get_height()
        pct = (h / len(y)) * 100
        ax.annotate(f"{h:,}\n({pct:.1f}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=11, fontweight="bold")
        
    ax.set_title("Target Class Distribution: Low CO vs High CO", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Number of Hourly Samples", fontsize=12)
    ax.set_ylim(0, max(counts.values) * 1.18)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "01_target_distribution_bar.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_target_pie(y, save_path=None):
    """Figure 2: Target distribution pie chart."""
    fig, ax = plt.subplots(figsize=(6, 6))
    counts = y.value_counts().sort_index()
    labels = ["Low CO (<= 4.0 mg/m³)", "High CO (> 4.0 mg/m³)"]
    colors = ["#10b981", "#ef4444"]
    explode = (0, 0.1)
    
    wedges, texts, autotexts = ax.pie(
        counts.values,
        explode=explode,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        textprops=dict(color=NAVY_COLOR, fontsize=11, fontweight="medium"),
        wedgeprops=dict(edgecolor="white", linewidth=2)
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(12)
        
    ax.set_title("Class Imbalance Proportion: Carbon Monoxide Pollution", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "02_target_distribution_pie.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_co_distribution(df, save_path=None):
    """Figure 3: Ground-truth CO concentration distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    co_vals = df[config.TARGET_RAW_COLUMN].dropna()
    
    sns.histplot(co_vals, bins=40, kde=True, color=PRIMARY_COLOR, ax=ax, edgecolor=NAVY_COLOR, alpha=0.6)
    ax.axvline(config.CO_HIGH_THRESHOLD, color="#ef4444", linestyle="--", linewidth=2,
               label=f"High CO Threshold ({config.CO_HIGH_THRESHOLD} mg/m³)")
    ax.axvline(co_vals.median(), color=ACCENT_COLOR, linestyle=":", linewidth=2,
               label=f"Median CO ({co_vals.median():.2f} mg/m³)")
    
    ax.set_title("Ground-Truth CO(GT) Concentration Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("CO Concentration (mg/m³)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.legend(frameon=True)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "03_co_concentration_distribution.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_temperature_distribution(df, save_path=None):
    """Figure 4: Temperature distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    t_vals = df["T"].dropna()
    
    sns.histplot(t_vals, bins=35, kde=True, color="#0284c7", ax=ax, edgecolor=NAVY_COLOR, alpha=0.6)
    ax.axvline(t_vals.mean(), color="#dc2626", linestyle="--", linewidth=2,
               label=f"Mean Temp ({t_vals.mean():.1f} °C)")
    
    ax.set_title("Ambient Temperature (T) Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Temperature (°C)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.legend(frameon=True)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "04_temperature_distribution.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_humidity_distribution(df, save_path=None):
    """Figure 5: Relative humidity distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    rh_vals = df["RH"].dropna()
    
    sns.histplot(rh_vals, bins=35, kde=True, color="#059669", ax=ax, edgecolor=NAVY_COLOR, alpha=0.6)
    ax.axvline(rh_vals.median(), color="#b45309", linestyle="--", linewidth=2,
               label=f"Median RH ({rh_vals.median():.1f} %)")
    
    ax.set_title("Relative Humidity (RH) Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Relative Humidity (%)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.legend(frameon=True)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "05_relative_humidity_distribution.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_nox_distribution(df, save_path=None):
    """Figure 6: NOx concentration distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    nox_vals = df["NOx(GT)"].dropna()
    
    sns.histplot(nox_vals, bins=45, kde=True, color="#7c3aed", ax=ax, edgecolor=NAVY_COLOR, alpha=0.6)
    ax.axvline(nox_vals.median(), color="#b45309", linestyle="--", linewidth=2,
               label=f"Median NOx ({nox_vals.median():.1f} ppb)")
    
    ax.set_title("Nitrogen Oxides NOx(GT) Concentration Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("NOx Concentration (ppb)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.legend(frameon=True)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "06_nox_distribution.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_no2_distribution(df, save_path=None):
    """Figure 7: NO2 concentration distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    no2_vals = df["NO2(GT)"].dropna()
    
    sns.histplot(no2_vals, bins=40, kde=True, color="#ea580c", ax=ax, edgecolor=NAVY_COLOR, alpha=0.6)
    ax.axvline(no2_vals.median(), color="#1e3a8a", linestyle="--", linewidth=2,
               label=f"Median NO2 ({no2_vals.median():.1f} µg/m³)")
    
    ax.set_title("Nitrogen Dioxide NO2(GT) Concentration Distribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("NO2 Concentration (µg/m³)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.legend(frameon=True)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "07_no2_distribution.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_correlation_heatmap(df, save_path=None):
    """Figure 8: Sensor feature correlation heatmap."""
    fig, ax = plt.subplots(figsize=(11, 9))
    cols = [c for c in config.BASE_PREDICTORS if c in df.columns]
    corr = df[cols].corr()
    
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    
    sns.heatmap(corr, mask=mask, cmap="coolwarm", vmin=-1, vmax=1, annot=True,
                fmt=".2f", linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title("Environmental Sensor Inter-Feature Correlation Heatmap", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "08_sensor_feature_correlation_heatmap.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_feature_target_correlation(df, y, save_path=None):
    """Figure 9: Feature correlation with the binary target."""
    fig, ax = plt.subplots(figsize=(10, 6))
    df_temp = df[config.ALL_PREDICTORS].copy()
    corrs = df_temp.apply(lambda col: col.corr(y)).dropna().sort_values()
    
    colors = [PRIMARY_COLOR if c > 0 else "#e11d48" for c in corrs.values]
    bars = ax.barh(corrs.index, corrs.values, color=colors, edgecolor=NAVY_COLOR, linewidth=0.8)
    
    for bar in bars:
        w = bar.get_width()
        offset = 0.02 if w >= 0 else -0.06
        ax.text(w + offset, bar.get_y() + bar.get_height()/2, f"{w:.2f}",
                va="center", fontsize=9, fontweight="bold")
        
    ax.axvline(0, color=NAVY_COLOR, linewidth=0.8, linestyle="--")
    ax.set_title("Predictor Feature Correlation with Binary Target (co_high)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Pearson Correlation Coefficient (r)", fontsize=12)
    ax.set_xlim(min(corrs.values) - 0.15, max(corrs.values) + 0.15)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "09_feature_correlation_with_target.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def plot_smote_comparison(y_train, save_path=None):
    """Figure 10: Class balance comparison before and after SMOTE."""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Simulate SMOTE on dummy labels for visual comparison
    counts_before = np.bincount(y_train)
    # SMOTE balances minority class to match majority class
    counts_after = [counts_before[0], counts_before[0]]
    
    x = np.arange(2)
    width = 0.35
    
    rects1 = ax.bar(x - width/2, counts_before, width, label="Before SMOTE (Training Set)",
                    color=["#64748b", "#f87171"], edgecolor=NAVY_COLOR)
    rects2 = ax.bar(x + width/2, counts_after, width, label="After SMOTE (Resampled Fold)",
                    color=["#0f766e", "#10b981"], edgecolor=NAVY_COLOR)
    
    for rects in [rects1, rects2]:
        for bar in rects:
            h = bar.get_height()
            ax.annotate(f"{h:,}",
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, fontweight="bold")
            
    ax.set_title("Training Set Class Distribution Before and After SMOTE", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(["Low CO (0)", "High CO (1)"], fontsize=11, fontweight="medium")
    ax.set_ylabel("Number of Samples", fontsize=12)
    ax.set_ylim(0, max(counts_after) * 1.15)
    ax.legend(frameon=True)
    plt.tight_layout()
    out = save_path or (config.IMAGES_DIR / "10_class_balance_before_after_smote.png")
    plt.savefig(out)
    plt.close()
    logger.info(f"Saved: {out.name}")
    return out


def generate_all_eda_visualizations(df_clean, df_engineered, y, y_train):
    """Run and save all 10 EDA visualizations."""
    logger.info("Generating 10 mandatory EDA visualizations...")
    plot_target_bar(y)
    plot_target_pie(y)
    plot_co_distribution(df_clean)
    plot_temperature_distribution(df_clean)
    plot_humidity_distribution(df_clean)
    plot_nox_distribution(df_clean)
    plot_no2_distribution(df_clean)
    plot_correlation_heatmap(df_clean)
    plot_feature_target_correlation(df_engineered, y)
    plot_smote_comparison(y_train)
    logger.info("All 10 EDA visualizations successfully generated.")


if __name__ == "__main__":
    from Source_Code.data_loader import load_raw_dataset
    from Source_Code.feature_engineering import derive_features
    from Source_Code.preprocessing import prepare_features_and_target, split_data
    
    df_raw, _ = load_raw_dataset()
    df_eng = derive_features(df_raw)
    X, y, df_valid = prepare_features_and_target(df_eng)
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    generate_all_eda_visualizations(df_valid, df_eng.loc[df_valid.index], y, y_train)
