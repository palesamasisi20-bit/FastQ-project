
from pathlib import Path
import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    classification_report,
)

from xgboost import XGBClassifier

DATA_DIR = Path("results/baselines")
OUT_DIR = DATA_DIR / "model_results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading assembled embeddings...")
train = np.load(DATA_DIR / "train_embeddings.npz")
val = np.load(DATA_DIR / "validation_embeddings.npz")
test = np.load(DATA_DIR / "test_embeddings.npz")

X_train, y_train = train["X"], train["y"]
X_val, y_val = val["X"], val["y"]
X_test, y_test = test["X"], test["y"]

encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_val = encoder.transform(y_val)
y_test = encoder.transform(y_test)

print("Classes:", list(encoder.classes_))
print("Train:", X_train.shape, "Validation:", X_val.shape, "Test:", X_test.shape)

models = {
    
    "RandomForest": RandomForestClassifier(
        n_estimators=200,
        max_features="sqrt",
        n_jobs=4,
        random_state=42
    ),
    "XGBoost": XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softprob",
        num_class=len(encoder.classes_),
        eval_metric="mlogloss",
        tree_method="hist",
        n_jobs=4,
        random_state=42
    ),
}

results = []

for name, model in models.items():
    print(f"\n{'=' * 60}\nTraining {name}")
    start = time.time()

    model.fit(X_train, y_train)
    val_pred = model.predict(X_val)

    val_accuracy = accuracy_score(y_val, val_pred)
    val_balanced = balanced_accuracy_score(y_val, val_pred)
    val_f1 = f1_score(y_val, val_pred, average="macro")

    print(f"Validation accuracy: {val_accuracy:.4f}")
    print(f"Validation balanced accuracy: {val_balanced:.4f}")
    print(f"Validation macro F1: {val_f1:.4f}")
    print(f"Time: {(time.time() - start) / 60:.1f} minutes")

    results.append({
        "model": name,
        "validation_accuracy": val_accuracy,
        "validation_balanced_accuracy": val_balanced,
        "validation_macro_f1": val_f1,
    })

    # Save each fitted model for reuse.
    import joblib
    joblib.dump(model, OUT_DIR / f"{name}.joblib")

results_df = pd.DataFrame(results)
results_df.to_csv(OUT_DIR / "validation_results.csv", index=False)

print("\nValidation comparison:")
print(results_df.sort_values("validation_macro_f1", ascending=False).to_string(index=False))
print(f"\nModels and results saved in {OUT_DIR}")
