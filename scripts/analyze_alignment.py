import csv

INPUT = "results/alignment_summary.csv"
OUTPUT = "results/alignment_analysis.csv"

# Read alignment summary
with open(INPUT, newline="") as f:
    rows = list(csv.DictReader(f))

# Find the clean/original dataset
original = next(
    row for row in rows
    if row["dataset"] == "sars_50k_original"
)

original_rate = float(original["mapping_rate"])

# Calculate change relative to original
for row in rows:
    rate = float(row["mapping_rate"])
    row["mapping_rate_change"] = round(rate - original_rate, 2)
    row["mapping_rate_drop"] = round(original_rate - rate, 2)

# Sort by largest mapping-rate drop
rows.sort(key=lambda x: x["mapping_rate_drop"], reverse=True)

# Write analysis table
fieldnames = [
    "dataset",
    "mapping_rate",
    "mapping_rate_change",
    "mapping_rate_drop"
]

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        writer.writerow({
            "dataset": row["dataset"],
            "mapping_rate": row["mapping_rate"],
            "mapping_rate_change": row["mapping_rate_change"],
            "mapping_rate_drop": row["mapping_rate_drop"]
        })

print(f"Original mapping rate: {original_rate:.2f}%")
print()
print("Mapping-rate comparison:")
print("-" * 65)

for row in rows:
    print(
        f"{row['dataset']:35s} "
        f"{float(row['mapping_rate']):6.2f}% "
        f"drop: {float(row['mapping_rate_drop']):5.2f}%"
    )

print()
print(f"Created {OUTPUT}")
