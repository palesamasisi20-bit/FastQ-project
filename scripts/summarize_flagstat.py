import glob
import re
import csv
import os

rows = []

for filepath in sorted(glob.glob("results/*.flagstat.txt")):
    name = os.path.basename(filepath).replace(".flagstat.txt", "")

    with open(filepath) as f:
        text = f.read()

    total = re.search(r"^(\d+) \+ 0 in total", text, re.MULTILINE)
    primary = re.search(r"^(\d+) \+ 0 primary$", text, re.MULTILINE)
    supplementary = re.search(r"^(\d+) \+ 0 supplementary$", text, re.MULTILINE)
    mapped = re.search(r"^(\d+) \+ 0 mapped \(([\d.]+)%", text, re.MULTILINE)

    rows.append({
        "dataset": name,
        "total": int(total.group(1)),
        "primary": int(primary.group(1)),
        "supplementary": int(supplementary.group(1)),
        "mapped": int(mapped.group(1)),
        "mapping_rate": float(mapped.group(2))
    })

with open("results/alignment_summary.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "dataset",
            "total",
            "primary",
            "supplementary",
            "mapped",
            "mapping_rate"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print("Created results/alignment_summary.csv")
