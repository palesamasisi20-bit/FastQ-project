from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    auc,
)
from sklearn.preprocessing import label_binarize


ROOT = Path(".")
RESULTS = ROOT / "results/baselines"
MODEL_DIR = RESULTS / "model_results"
FIG_DIR = RESULTS / "figures"

FIG_DIR.mkdir(parents=True, exist_ok=True)

TEST_FILE = RESULTS / "test_embeddings.npz"

# Use the established class names and their encoded labels.
CLASS_NAMES = [
    "adapter_insertion",
    "deletion",
    "insertion",
    "low_complexity",
    "nmasking",
    "original",
    "substitution",
]

LABEL_TO_ID = {
    name: i for i, name in enumerate(CLASS_NAMES)
}

MODELS = [
    "LogisticRegression",
    "RandomForest",
    "XGBoost",
]

if not TEST_FILE.exists():
    raise FileNotFoundError(
        f"Test embeddings not found: {TEST_FILE}"
    )

print(f"Loading test data: {TEST_FILE}")

test = np.load(TEST_FILE, allow_pickle=True)
X_test = test["X"]
y_raw = test["y"]

# Convert string labels to the same integer encoding used
# by the saved classifiers.
if np.issubdtype(y_raw.dtype, np.number):
    y_test = y_raw.astype(int)
else:
    unknown = sorted(set(y_raw.tolist()) - set(CLASS_NAMES))
    if unknown:
        raise ValueError(f"Unknown test labels: {unknown}")

    y_test = np.array(
        [LABEL_TO_ID[str(label)] for label in y_raw],
        dtype=int,
    )

expected_ids = set(range(len(CLASS_NAMES)))
if set(np.unique(y_test)) != expected_ids:
    raise ValueError(
        "The test labels do not contain all seven expected classes."
    )

y_binary = label_binarize(
    y_test,
    classes=np.arange(len(CLASS_NAMES)),
)

summary_rows = []
class_rows = []
roc_data = {}

for model_name in MODELS:
    model_path = MODEL_DIR / f"{model_name}.joblib"

    if not model_path.exists():
        print(f"Skipping missing model: {model_path}")
        continue

    print(f"Calculating AUROC for {model_name}...")
    model = joblib.load(model_path)

    if not hasattr(model, "predict_proba"):
        print(f"Skipping {model_name}: no predict_proba method.")
        continue

    probabilities = model.predict_proba(X_test)
    model_classes = np.asarray(model.classes_)

    # Arrange probability columns in the established class order.
    if set(model_classes.tolist()) != expected_ids:
        raise ValueError(
            f"Unexpected model classes for {model_name}: "
            f"{model_classes}"
        )

    column_order = [
        int(np.where(model_classes == i)[0][0])
        for i in range(len(CLASS_NAMES))
    ]
    probabilities = probabilities[:, column_order]

    macro_auc = roc_auc_score(
        y_binary,
        probabilities,
        average="macro",
    )
    weighted_auc = roc_auc_score(
        y_binary,
        probabilities,
        average="weighted",
    )

    summary_rows.append({
        "model": model_name,
        "test_macro_ovr_auroc": macro_auc,
        "test_weighted_ovr_auroc": weighted_auc,
    })

    roc_data[model_name] = (y_binary, probabilities)

    for i, class_name in enumerate(CLASS_NAMES):
        class_auc = roc_auc_score(
            y_binary[:, i],
            probabilities[:, i],
        )

        class_rows.append({
            "model": model_name,
            "class": class_name,
            "test_ovr_auroc": class_auc,
        })

        print(f"  {class_name}: {class_auc:.4f}")

    print(
        f"  Macro AUROC: {macro_auc:.4f}\n"
        f"  Weighted AUROC: {weighted_auc:.4f}"
    )

if not summary_rows:
    raise RuntimeError("No models were successfully evaluated.")

summary = pd.DataFrame(summary_rows)
per_class = pd.DataFrame(class_rows)

summary_path = MODEL_DIR / "test_auroc_all_models.csv"
class_path = MODEL_DIR / "test_auroc_per_class.csv"

summary.to_csv(summary_path, index=False)
per_class.to_csv(class_path, index=False)

# Plot overall macro AUROC.
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    summary["model"],
    summary["test_macro_ovr_auroc"],
)
ax.set_ylim(0, 1)
ax.set_ylabel("Macro one-vs-rest AUROC")
ax.set_xlabel("Classifier")
ax.set_title("Frozen Embeddings: Test AUROC Comparison")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()

overall_plot = FIG_DIR / "test_auroc_comparison.png"
fig.savefig(overall_plot, dpi=300)
plt.close(fig)

# Plot per-class AUROC.
pivot = per_class.pivot(
    index="class",
    columns="model",
    values="test_ovr_auroc",
)

ax = pivot.plot(kind="bar", figsize=(12, 6), ylim=(0, 1))
ax.set_ylabel("One-vs-rest AUROC")
ax.set_xlabel("Class")
ax.set_title("Test AUROC by Corruption Class")
ax.tick_params(axis="x", rotation=35)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()

class_plot = FIG_DIR / "test_auroc_per_class.png"
plt.savefig(class_plot, dpi=300)
plt.close()

print("\nAUROC analysis complete.")
print(f"Overall results: {summary_path}")
print(f"Per-class results: {class_path}")
print(f"Figures: {overall_plot}, {class_plot}")
