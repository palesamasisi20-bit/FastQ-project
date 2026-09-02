import csv

mapping_file = "results/alignment_analysis.csv"
stats_file = "results/alignment_stats.csv"
output_file = "results/alignment_baseline.csv"

# Read mapping-rate analysis
with open(mapping_file, newline="") as f:
    mapping_rows = {
        row["dataset"]: row
        for row in csv.DictReader(f)
    }

# Read detailed alignment statistics
with open(stats_file, newline="") as f:
    stats_rows = {
        row["dataset"]: row
        for row in csv.DictReader(f)
    }

datasets = sorted(mapping_rows.keys())

fields = [
    "dataset",
    "mapping_rate",
    "mapping_rate_drop_pp",
    "error_rate_percent",
    "error_rate_increase_pp",
    "reads_mapped",
    "reads_unmapped",
    "mismatches",
    "supplementary_alignments"
]

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for dataset in datasets:
        mapping = mapping_rows[dataset]
        stats = stats_rows[dataset]

        writer.writerow({
            "dataset": dataset,
            "mapping_rate": mapping["mapping_rate"],
            "mapping_rate_drop_pp": mapping["mapping_rate_drop"],
            "error_rate_percent": float(stats["error_rate"]) * 100,
            "error_rate_increase_pp":
                (float(stats["error_rate"]) * 100)
                - (float(stats_rows["sars_50k_original"]["error_rate"]) * 100),
            "reads_mapped": stats["reads_mapped"],
            "reads_unmapped": stats["reads_unmapped"],
            "mismatches": stats["mismatches"],
            "supplementary_alignments": stats["supplementary_alignments"]
        })

print(f"Created {output_file}")
print(f"Datasets included: {len(datasets)}")
