"""
Model evaluation, metrics computation, and performance visualization module for AI-ML-060:
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
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from Source_Code.utils import logger, save_json, save_model, load_json

PRIMARY_COLOR = "#0f766e"    # Teal
SECONDARY_COLOR = "#1b4934"  # Dark Forest Green
ACCENT_COLOR = "#d97706"     # Amber
NAVY_COLOR = "#1e293b"       # Dark Navy

sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300


def evaluate_classifier_model(name, pipeline, X_test, y_test):
    """Evaluate a classification pipeline on held-out test data."""
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec_w = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec_w = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1_w = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    
    # Supplementary positive-class (High CO) specific metrics
    prec_pos = precision_score(y_test, y_pred, pos_label=1, zero_division=0)
    rec_pos = recall_score(y_test, y_pred, pos_label=1, zero_division=0)
    f1_pos = f1_score(y_test, y_pred, pos_label=1, zero_division=0)
    
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred).tolist()
    clf_rep_dict = classification_report(y_test, y_pred, target_names=["Low CO (0)", "High CO (1)"], output_dict=True)
    clf_rep_txt = classification_report(y_test, y_pred, target_names=["Low CO (0)", "High CO (1)"])
    
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    
    return {
        "model_name": name,
        "accuracy": float(acc),
        "precision_weighted": float(prec_w),
        "recall_weighted": float(rec_w),
        "f1_weighted": float(f1_w),
        "precision_positive_class": float(prec_pos),
        "recall_positive_class": float(rec_pos),
        "f1_positive_class": float(f1_pos),
        "roc_auc": float(auc),
        "confusion_matrix": cm,
        "classification_report_dict": clf_rep_dict,
        "classification_report_text": clf_rep_txt,
        "fpr": [float(x) for x in fpr],
        "tpr": [float(x) for x in tpr],
        "y_pred": [int(x) for x in y_pred],
        "y_proba": [float(x) for x in y_proba],
    }


def evaluate_all_models(models, X_test, y_test):
    """
    Evaluate all models, save comparison tables, classification reports,
    generate all required evaluation plots, and select the best model.
    """
    logger.info("Evaluating models on held-out test set...")
    results = {}
    
    for name in ["Model_A_L1", "Model_B_L2"]:
        if name in models:
            results[name] = evaluate_classifier_model(name, models[name], X_test, y_test)
            logger.info(f"{name} Test Set Evaluation: Accuracy={results[name]['accuracy']:.4f}, "
                        f"F1-Weighted={results[name]['f1_weighted']:.4f}, "
                        f"High-CO F1={results[name]['f1_positive_class']:.4f}, "
                        f"ROC-AUC={results[name]['roc_auc']:.4f}")
            
    # Continuous regression baselines evaluation (with 0.5 threshold)
    for reg_name in ["Reg_Lasso", "Reg_Ridge"]:
        if reg_name in models:
            preds_cont = models[reg_name].predict(X_test)
            preds_bin = (preds_cont >= 0.5).astype(int)
            acc = accuracy_score(y_test, preds_bin)
            f1_w = f1_score(y_test, preds_bin, average="weighted", zero_division=0)
            f1_pos = f1_score(y_test, preds_bin, pos_label=1, zero_division=0)
            cm = confusion_matrix(y_test, preds_bin).tolist()
            results[reg_name] = {
                "model_name": reg_name,
                "accuracy": float(acc),
                "f1_weighted": float(f1_w),
                "f1_positive_class": float(f1_pos),
                "confusion_matrix": cm,
                "decision_threshold": 0.5,
            }
            logger.info(f"{reg_name} (Threshold 0.5): Accuracy={acc:.4f}, F1-Weighted={f1_w:.4f}")

    # Build model comparison table
    comparison_rows = []
    for k in ["Model_A_L1", "Model_B_L2"]:
        res = results[k]
        comparison_rows.append({
            "Model": "Model A (L1 Regularized / Lasso Logistic)",
            "Accuracy": res["accuracy"],
            "Precision (Weighted)": res["precision_weighted"],
            "Recall (Weighted)": res["recall_weighted"],
            "F1-Score (Weighted)": res["f1_weighted"],
            "High-CO Precision": res["precision_positive_class"],
            "High-CO Recall": res["recall_positive_class"],
            "High-CO F1-Score": res["f1_positive_class"],
            "ROC-AUC": res["roc_auc"],
        } if k == "Model_A_L1" else {
            "Model": "Model B (L2 Regularized / Ridge Logistic)",
            "Accuracy": res["accuracy"],
            "Precision (Weighted)": res["precision_weighted"],
            "Recall (Weighted)": res["recall_weighted"],
            "F1-Score (Weighted)": res["f1_weighted"],
            "High-CO Precision": res["precision_positive_class"],
            "High-CO Recall": res["recall_positive_class"],
            "High-CO F1-Score": res["f1_positive_class"],
            "ROC-AUC": res["roc_auc"],
        })
        
    df_comp = pd.DataFrame(comparison_rows)
    df_comp.to_csv(config.METRICS_DIR / "model_comparison.csv", index=False)
    save_json(results, config.METRICS_DIR / "model_comparison.json")
    
    # Save classification reports text
    rep_txt = (
        "=======================================================\n"
        "AI-ML-060: MODEL CLASSIFICATION PERFORMANCE REPORTS\n"
        "Held-Out Test Set (20% Stratified Split, N = 1535)\n"
        "=======================================================\n\n"
        "1. MODEL A: LASSO-STYLE L1 REGULARIZED LOGISTIC REGRESSION (C=100.0, liblinear)\n"
        "-------------------------------------------------------\n"
        f"{results['Model_A_L1']['classification_report_text']}\n"
        f"ROC-AUC Score: {results['Model_A_L1']['roc_auc']:.4f}\n\n"
        "2. MODEL B: RIDGE-STYLE L2 REGULARIZED LOGISTIC REGRESSION (C=1.0, lbfgs)\n"
        "-------------------------------------------------------\n"
        f"{results['Model_B_L2']['classification_report_text']}\n"
        f"ROC-AUC Score: {results['Model_B_L2']['roc_auc']:.4f}\n"
    )
    with open(config.METRICS_DIR / "classification_reports.txt", "w", encoding="utf-8") as f:
        f.write(rep_txt)
        
    # Determine best model based on F1-weighted / ROC-AUC
    score_a = results["Model_A_L1"]["f1_weighted"] + results["Model_A_L1"]["roc_auc"]
    score_b = results["Model_B_L2"]["f1_weighted"] + results["Model_B_L2"]["roc_auc"]
    best_name = "Model_A_L1" if score_a >= score_b else "Model_B_L2"
    best_pipeline = models[best_name]
    save_model(best_pipeline, config.MODELS_DIR / "best_model.joblib")
    logger.info(f"Selected Best Model: {best_name} (saved to models/best_model.joblib)")
    
    # Generate Visualizations 11-17
    generate_evaluation_visualizations(results, models, X_test.columns)
    
    return results, best_name


def generate_evaluation_visualizations(results, models, feature_names):
    """Generate figures 11 to 17."""
    res_a = results["Model_A_L1"]
    res_b = results["Model_B_L2"]
    
    # Figure 11: Model Accuracy Comparison
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Model A\n(L1 Lasso-style)", "Model B\n(L2 Ridge-style)"]
    accs = [res_a["accuracy"] * 100, res_b["accuracy"] * 100]
    bars = ax.bar(labels, accs, color=[PRIMARY_COLOR, "#0284c7"], width=0.45, edgecolor=NAVY_COLOR, linewidth=1.2)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 5), textcoords="offset points", ha="center", va="bottom",
                    fontsize=12, fontweight="bold")
        
    ax.axhline(85.0, color="#ef4444", linestyle="--", linewidth=1.5, label="Target Benchmark (85%)")
    ax.set_title("Test Set Classification Accuracy Comparison", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Accuracy (%)", fontsize=12)
    ax.set_ylim(0, 105)
    ax.legend(frameon=True, loc="lower right")
    plt.tight_layout()
    plt.savefig(config.IMAGES_DIR / "11_model_accuracy_comparison.png")
    plt.close()
    logger.info("Saved: 11_model_accuracy_comparison.png")
    
    # Figure 12: Precision, Recall, F1 Comparison
    fig, ax = plt.subplots(figsize=(9, 5))
    metrics_names = ["Accuracy", "Weighted Precision", "Weighted Recall", "Weighted F1", "ROC-AUC"]
    vals_a = [res_a["accuracy"], res_a["precision_weighted"], res_a["recall_weighted"], res_a["f1_weighted"], res_a["roc_auc"]]
    vals_b = [res_b["accuracy"], res_b["precision_weighted"], res_b["recall_weighted"], res_b["f1_weighted"], res_b["roc_auc"]]
    
    x = np.arange(len(metrics_names))
    width = 0.35
    rects1 = ax.bar(x - width/2, vals_a, width, label="Model A (L1 Lasso-style)", color=PRIMARY_COLOR, edgecolor=NAVY_COLOR)
    rects2 = ax.bar(x + width/2, vals_b, width, label="Model B (L2 Ridge-style)", color="#0284c7", edgecolor=NAVY_COLOR)
    
    for rects in [rects1, rects2]:
        for bar in rects:
            h = bar.get_height()
            ax.annotate(f"{h:.3f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                        fontsize=9, fontweight="bold")
            
    ax.set_title("Multi-Metric Model Performance Comparison on Held-Out Test Set", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=10, fontweight="medium")
    ax.set_ylabel("Metric Value (0.0 - 1.0)", fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.legend(frameon=True, loc="lower left")
    plt.tight_layout()
    plt.savefig(config.IMAGES_DIR / "12_precision_recall_f1_comparison.png")
    plt.close()
    logger.info("Saved: 12_precision_recall_f1_comparison.png")
    
    # Figure 13: Confusion Matrices for both models
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    cm_a = np.array(res_a["confusion_matrix"])
    cm_b = np.array(res_b["confusion_matrix"])
    class_labels = ["Low CO (0)", "High CO (1)"]
    
    sns.heatmap(cm_a, annot=True, fmt="d", cmap="Blues", ax=axes[0],
                xticklabels=class_labels, yticklabels=class_labels, cbar=False)
    axes[0].set_title("Model A: L1 Regularized Confusion Matrix", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Predicted Label", fontsize=11)
    axes[0].set_ylabel("True Label", fontsize=11)
    
    sns.heatmap(cm_b, annot=True, fmt="d", cmap="Greens", ax=axes[1],
                xticklabels=class_labels, yticklabels=class_labels, cbar=False)
    axes[1].set_title("Model B: L2 Regularized Confusion Matrix", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Predicted Label", fontsize=11)
    axes[1].set_ylabel("True Label", fontsize=11)
    
    plt.tight_layout()
    plt.savefig(config.IMAGES_DIR / "13_confusion_matrix_comparison.png")
    plt.close()
    logger.info("Saved: 13_confusion_matrix_comparison.png")
    
    # Figure 14: ROC Curves
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(res_a["fpr"], res_a["tpr"], color=PRIMARY_COLOR, lw=2.5,
            label=f"Model A (L1 Lasso-style) — AUC = {res_a['roc_auc']:.4f}")
    ax.plot(res_b["fpr"], res_b["tpr"], color="#0284c7", lw=2.5, linestyle="--",
            label=f"Model B (L2 Ridge-style) — AUC = {res_b['roc_auc']:.4f}")
    ax.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle=":", label="Random Guess (AUC = 0.5000)")
    
    ax.set_title("Receiver Operating Characteristic (ROC) Curves", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
    ax.set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=12)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.05])
    ax.legend(frameon=True, loc="lower right", fontsize=11)
    plt.tight_layout()
    plt.savefig(config.IMAGES_DIR / "14_roc_curves.png")
    plt.close()
    logger.info("Saved: 14_roc_curves.png")
    
    # Figure 15: Feature Importance Coefficients (Top 15 by absolute magnitude)
    fig, ax = plt.subplots(figsize=(10, 7))
    model_b_clf = models["Model_B_L2"].named_steps["classifier"]
    coefs = model_b_clf.coef_[0]
    
    feat_df = pd.DataFrame({"Feature": feature_names, "Coefficient": coefs})
    feat_df["Abs_Coef"] = feat_df["Coefficient"].abs()
    top15 = feat_df.sort_values(by="Abs_Coef", ascending=False).head(15).sort_values(by="Coefficient")
    
    colors = [PRIMARY_COLOR if c > 0 else "#e11d48" for c in top15["Coefficient"]]
    bars = ax.barh(top15["Feature"], top15["Coefficient"], color=colors, edgecolor=NAVY_COLOR, linewidth=0.8)
    
    for bar in bars:
        w = bar.get_width()
        offset = 0.03 if w >= 0 else -0.09
        ax.text(w + offset, bar.get_y() + bar.get_height()/2, f"{w:.3f}",
                va="center", fontsize=9, fontweight="bold")
        
    ax.axvline(0, color=NAVY_COLOR, linestyle="--", linewidth=0.8)
    ax.set_title("Top 15 Model Predictor Coefficients (Standardized Scale)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Logistic Regression Coefficient Magnitude (Beta)", fontsize=12)
    ax.set_xlim(min(top15["Coefficient"]) - 0.2, max(top15["Coefficient"]) + 0.2)
    plt.tight_layout()
    plt.savefig(config.IMAGES_DIR / "15_feature_importance_coefficients.png")
    plt.close()
    logger.info("Saved: 15_feature_importance_coefficients.png")
    
    # Figure 16: Cross-validation scores comparison
    cv_data_path = config.METRICS_DIR / "cross_validation.json"
    if cv_data_path.exists():
        cv_json = load_json(cv_data_path)
        fig, ax = plt.subplots(figsize=(8, 5))
        folds = [f"Fold {i+1}" for i in range(config.CV_FOLDS)]
        scores_a = cv_json["Model_A_L1_LassoStyle"]["accuracy"]["folds"]
        scores_b = cv_json["Model_B_L2_RidgeStyle"]["accuracy"]["folds"]
        
        x = np.arange(len(folds))
        width = 0.35
        ax.bar(x - width/2, [s * 100 for s in scores_a], width, label="Model A (L1)", color=PRIMARY_COLOR, edgecolor=NAVY_COLOR)
        ax.bar(x + width/2, [s * 100 for s in scores_b], width, label="Model B (L2)", color="#0284c7", edgecolor=NAVY_COLOR)
        
        ax.axhline(np.mean(scores_a)*100, color=PRIMARY_COLOR, linestyle="--", alpha=0.7,
                   label=f"Model A Mean ({np.mean(scores_a)*100:.2f}%)")
        ax.axhline(np.mean(scores_b)*100, color="#0284c7", linestyle=":", alpha=0.7,
                   label=f"Model B Mean ({np.mean(scores_b)*100:.2f}%)")
        
        ax.set_title("5-Fold Stratified Cross-Validation Accuracy Across Folds", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(folds, fontsize=11)
        ax.set_ylabel("Accuracy (%)", fontsize=12)
        ax.set_ylim(min(min(scores_a), min(scores_b))*100 - 5, 102)
        ax.legend(frameon=True, loc="lower right")
        plt.tight_layout()
        plt.savefig(config.IMAGES_DIR / "16_cross_validation_scores.png")
        plt.close()
        logger.info("Saved: 16_cross_validation_scores.png")
        
    # Figure 17: Learning Curves (Train vs Validation)
    lc_data_path = config.METRICS_DIR / "learning_curves.json"
    if lc_data_path.exists():
        lc_json = load_json(lc_data_path)
        fig, ax = plt.subplots(figsize=(8, 5))
        train_sizes = lc_json["train_sizes"]
        
        m_a_train = lc_json["Model_A"]["train_mean"]
        m_a_val = lc_json["Model_A"]["val_mean"]
        m_b_train = lc_json["Model_B"]["train_mean"]
        m_b_val = lc_json["Model_B"]["val_mean"]
        
        ax.plot(train_sizes, m_a_train, "o-", color=PRIMARY_COLOR, label="Model A (L1) - Training F1")
        ax.plot(train_sizes, m_a_val, "s--", color="#0d9488", label="Model A (L1) - Validation F1")
        ax.plot(train_sizes, m_b_train, "^-", color="#1e40af", label="Model B (L2) - Training F1")
        ax.plot(train_sizes, m_b_val, "d--", color="#38bdf8", label="Model B (L2) - Validation F1")
        
        ax.set_title("Model Learning Curves: Training vs Validation Weighted F1-Score", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Number of Training Samples", fontsize=11)
        ax.set_ylabel("Weighted F1-Score", fontsize=11)
        ax.set_ylim([0.70, 1.02])
        ax.legend(frameon=True, loc="lower right")
        plt.tight_layout()
        plt.savefig(config.IMAGES_DIR / "17_learning_curves.png")
        plt.close()
        logger.info("Saved: 17_learning_curves.png")


if __name__ == "__main__":
    from Source_Code.data_loader import load_raw_dataset
    from Source_Code.feature_engineering import derive_features
    from Source_Code.preprocessing import prepare_features_and_target, split_data
    from Source_Code.model_training import train_and_cross_validate_models
    
    df_raw, _ = load_raw_dataset()
    df_eng = derive_features(df_raw)
    X, y, _ = prepare_features_and_target(df_eng)
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    models, _, _ = train_and_cross_validate_models(X_train, y_train)
    results, best_model_name = evaluate_all_models(models, X_test, y_test)
    print("\nEvaluation & Visualization Generation Completed Successfully.")
