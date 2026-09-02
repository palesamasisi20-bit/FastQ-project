import subprocess
import csv
import glob
import os

output = "results/alignment_stats.csv"

fields = [
    "dataset",
    "reads",
    "reads_mapped",
    "reads_unmapped",
    "supplementary_alignments",
    "bases_mapped",
    "mismatches",
    "error_rate",
    "average_read_length",
    "maximum_read_length"
]

rows = []

for bam in sorted(glob.glob("results/*.sorted.bam")):

    dataset = os.path.basename(bam).replace(".sorted.bam", "")

    result = subprocess.run(
        ["samtools", "stats", bam],
        capture_output=True,
        text=True,
        check=True
    )

    stats = {}

    for line in result.stdout.splitlines():
        if line.startswith("SN"):
            parts = line.split("\t")

            if len(parts) >= 3:
                key = parts[1].rstrip(":")
                value = parts[2]

                stats[key] = value

    rows.append({
        "dataset": dataset,
        "reads": stats.get("raw total sequences", ""),
        "reads_mapped": stats.get("reads mapped", ""),
        "reads_unmapped": stats.get("reads unmapped", ""),
        "supplementary_alignments": stats.get("supplementary alignments", ""),
        "bases_mapped": stats.get("bases mapped", ""),
        "mismatches": stats.get("mismatches", ""),
        "error_rate": stats.get("error rate", ""),
        "average_read_length": stats.get("average length", ""),
        "maximum_read_length": stats.get("maximum length", "")
    })

with open(output, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Created {output}")
print(f"Datasets analysed: {len(rows)}")
