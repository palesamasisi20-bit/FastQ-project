import csv
import matplotlib.pyplot as plt

INPUT = "results/error_rate_analysis.csv"
OUTPUT = "results/error_rate_comparison.png"

datasets = []
changes = []

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        datasets.append(row["dataset"].replace("sars_50k_", ""))
        changes.append(float(row["change_from_original_pp"]))

plt.figure(figsize=(10, 6))

plt.bar(datasets, changes)

plt.ylabel("Increase in error rate (percentage points)")
plt.xlabel("Dataset")
plt.title("Alignment Error Rate Increase Relative to Original Reads")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()
plt.savefig(OUTPUT, dpi=300)

print(f"Created {OUTPUT}")
