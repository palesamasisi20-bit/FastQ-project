from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


# --------------------------------------------------
# 1. Locate project files
# --------------------------------------------------

ROOT = Path(".")
FIG_DIR = ROOT / "results" / "baselines" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Support both the original results folder and the
# folder used to transfer results from ilifu.
model_dir_options = [
    ROOT / "results" / "baselines" / "model_results",
    ROOT / "transfer_baseline" / "Model_results",
    ROOT / "transfer_baseline" / "model_results",
]

MODEL_DIR = next(
    (p for p in model_dir_options if p.exists()),
    None
)

if MODEL_DIR is None:
    raise FileNotFoundError(
        "Could not find model_results or Model_results. "
        "Check the folder containing the .joblib files."
    )

embedding_options = [
    ROOT / "results" / "baselines" / "test_embeddings.npz",
    ROOT / "transfer_baseline" / "test_embeddings.npz",
]

TEST_FILE = next(
    (p for p in embedding_options if p.exists()),
    None
)

summary_file = MODEL_DIR / "test_results_all_models.csv"

if not summary_file.exists():
    raise FileNotFoundError(
        f"Could not find test_results_all_models.csv in {MODEL_DIR}"
    )

print(f"Models and reports: {MODEL_DIR}")
print(f"Figures will be saved in: {FIG_DIR}")


# --------------------------------------------------
# 2. Overall model performance comparison
# --------------------------------------------------

df = pd.read_csv(summary_file)

metrics = [
    "test_accuracy",
    "test_balanced_accuracy",
    "test_macro_f1",
]

metric_labels = {
    "test_accuracy": "Accuracy",
    "test_balanced_accuracy": "Balanced accuracy",
    "test_macro_f1": "Macro F1",
}

available = [m for m in metrics if m in df.columns]

if not available:
    raise ValueError(
        "No expected test metrics found. CSV columns are: "
        f"{df.columns.tolist()}"
    )

if "model" not in df.columns:
    raise ValueError(
        "Expected a 'model' column in test_results_all_models.csv."
    )

plot_df = df.set_index("model")[available]
plot_df = plot_df.rename(columns=metric_labels)

ax = plot_df.plot(
    kind="bar",
    figsize=(10, 6),
    ylim=(0, 1),
)

ax.set_title("Frozen Nucleotide Transformer Embeddings: Test Performance")
ax.set_ylabel("Score")
ax.set_xlabel("Classifier")
ax.tick_params(axis="x", rotation=0)
ax.legend(loc="lower right")
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(FIG_DIR / "test_metrics_comparison.png", dpi=300)
plt.close()

print("Saved overall model comparison.")


# --------------------------------------------------
# 3. Per-class precision, recall and F1-score
# --------------------------------------------------

class_names = [
    "adapter_insertion",
    "deletion",
    "insertion",
    "low_complexity",
    "nmasking",
    "original",
    "substitution",
]

report_files = sorted(
    MODEL_DIR.glob("*_test_classification_report.csv")
)

for report_file in report_files:
    report = pd.read_csv(report_file, index_col=0)
    report.index = report.index.astype(str)

    # Keep only the seven class rows.
    class_report = report.reindex(class_names)
    class_report = class_report.dropna(subset=["f1-score"])

    if class_report.empty:
        print(f"Skipped report with unexpected labels: {report_file.name}")
        continue

    columns = [
        c for c in ["precision", "recall", "f1-score"]
        if c in class_report.columns
    ]

    ax = class_report[columns].plot(
        kind="bar",
        figsize=(12, 6),
        ylim=(0, 1),
    )

    ax.set_title(
        "Per-class performance: "
        + report_file.stem.replace(
            "_test_classification_report", ""
        )
    )
    ax.set_ylabel("Score")
    ax.set_xlabel("Corruption class")
    ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_file = FIG_DIR / f"{report_file.stem}_per_class.png"
    plt.savefig(output_file, dpi=300)
    plt.close()

    print(f"Saved {output_file}")


# --------------------------------------------------
# 4. Confusion matrices
# --------------------------------------------------

if TEST_FILE is None:
    print(
        "WARNING: test_embeddings.npz was not found. "
        "Confusion matrices will be skipped."
    )
else:
    print(f"Loading test embeddings from: {TEST_FILE}")

    with np.load(TEST_FILE, allow_pickle=True) as test_data:
        X_test = test_data["X"]
        y_test = test_data["y"]

    # Convert labels to a consistent text representation.
    y_test = np.asarray(y_test).reshape(-1)

    if len(X_test) != len(y_test):
        raise ValueError(
            f"Number of embeddings ({len(X_test)}) does not match "
            f"number of labels ({len(y_test)})."
        )

    # LabelEncoder normally maps alphabetically sorted class names
    # to 0, 1, 2, ... . Use that mapping if y_test contains strings
    # and a model predicts integer labels.
    if y_test.dtype.kind in {"U", "S", "O"}:
        y_test_text = y_test.astype(str)
        sorted_labels = sorted(np.unique(y_test_text).tolist())
        numeric_to_text = {
            i: name for i, name in enumerate(sorted_labels)
        }
    else:
        y_test_text = y_test
        numeric_to_text = {
            i: name for i, name in enumerate(class_names)
        }

    for model_name in [
        "LogisticRegression",
        "RandomForest",
        "XGBoost",
    ]:
        model_path = MODEL_DIR / f"{model_name}.joblib"

        if not model_path.exists():
            print(f"Model not found, skipping: {model_path}")
            continue

        print(f"Generating confusion matrix for {model_name}...")

        model = joblib.load(model_path)
        predictions = np.asarray(model.predict(X_test)).reshape(-1)

        if len(predictions) != len(y_test_text):
            raise ValueError(
                f"Prediction count mismatch for {model_name}."
            )

        # Align predicted labels with the test labels.
        if y_test.dtype.kind in {"U", "S", "O"}:
            if predictions.dtype.kind in {"i", "u", "f"}:
                try:
                    predictions_text = np.array([
                        numeric_to_text[int(p)] for p in predictions
                    ])
                except (KeyError, ValueError):
                    raise ValueError(
                        f"Could not map numeric predictions from "
                        f"{model_name} to the test class names. "
                        "Check the label encoding used during training."
                    )
            else:
                predictions_text = predictions.astype(str)

            labels = sorted(np.unique(y_test_text).tolist())
            true_labels = y_test_text
            predicted_labels = predictions_text

        else:
            true_labels = y_test
            predicted_labels = predictions
            labels = sorted(np.unique(y_test).tolist())

        cm = confusion_matrix(
            true_labels,
            predicted_labels,
            labels=labels,
        )

        display_labels = [str(label) for label in labels]

        fig, ax = plt.subplots(figsize=(10, 8))

        display = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=display_labels,
        )

        display.plot(
            ax=ax,
            xticks_rotation=45,
            colorbar=False,
            values_format="d",
        )

        ax.set_title(f"{model_name}: Test Confusion Matrix")
        plt.tight_layout()

        output_file = FIG_DIR / f"{model_name}_confusion_matrix.png"
        plt.savefig(output_file, dpi=300)
        plt.close(fig)

        print(f"Saved {output_file}")


# --------------------------------------------------
# 5. List the figures produced
# --------------------------------------------------

print("\nPlotting finished.")
print(f"Figure directory: {FIG_DIR}")

for figure in sorted(FIG_DIR.glob("*.png")):
    print(f"{figure} ({figure.stat().st_size / 1024:.1f} KB)")
