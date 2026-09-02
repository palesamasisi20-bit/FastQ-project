import csv
import matplotlib.pyplot as plt

INPUT = "results/alignment_analysis.csv"
OUTPUT = "results/mapping_rate_comparison.png"

datasets = []
mapping_rates = []

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        datasets.append(row["dataset"].replace("sars_50k_", ""))
        mapping_rates.append(float(row["mapping_rate"]))

plt.figure(figsize=(10, 6))

plt.bar(datasets, mapping_rates)

plt.ylabel("Mapping rate (%)")
plt.xlabel("Dataset")
plt.title("Mapping Rate Across Original and Corrupted FASTQ Datasets")

plt.xticks(rotation=45, ha="right")
plt.ylim(90, 100)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=300)

print(f"Created {OUTPUT}")
