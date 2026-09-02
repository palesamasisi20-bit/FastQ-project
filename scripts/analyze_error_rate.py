import csv

INPUT = "results/alignment_stats.csv"
OUTPUT = "results/error_rate_analysis.csv"

rows = []

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)
    data = list(reader)

original = next(
    row for row in data
    if row["dataset"] == "sars_50k_original"
)

original_error = float(original["error_rate"]) * 100

for row in data:
    error_rate = float(row["error_rate"]) * 100
    change = error_rate - original_error

    rows.append({
        "dataset": row["dataset"],
        "error_rate_percent": round(error_rate, 4),
        "change_from_original_pp": round(change, 4)
    })

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "dataset",
            "error_rate_percent",
            "change_from_original_pp"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print(f"Created {OUTPUT}")
