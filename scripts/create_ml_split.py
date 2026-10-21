import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from Bio import SeqIO

manifest_path = Path("results/dataset_manifest.csv")
original_path = Path("data/sars_50k.fastq")
output_path = Path("results/ml_dataset_manifest_70_15_15.csv")

manifest = pd.read_csv(manifest_path)

required = {"fastq_file", "label"}
if not required.issubset(manifest.columns):
    raise ValueError(f"Manifest must contain columns: {required}")

if not original_path.is_file():
    raise FileNotFoundError(original_path)

# Load only the extracted 50,000-record dataset.
original_records = list(SeqIO.parse(str(original_path), "fastq"))

if len(original_records) != 50000:
    raise ValueError(
        f"Expected 50,000 extracted records; found {len(original_records)}."
    )

def spot_key(record):
    # Sequencing instrument coordinates are shared by records
    # belonging to the same sequencing spot.
    fields = record.description.split()
    if len(fields) < 2:
        raise ValueError(f"Cannot identify sequencing spot: {record.description}")
    return fields[1]

original_keys = [spot_key(r) for r in original_records]

# Group record positions by sequencing spot, not read ID alone.
spot_positions = defaultdict(list)
for index, key in enumerate(original_keys):
    spot_positions[key].append(index)

# Verify every dataset matches the original record order and spot groups.
for _, dataset in manifest.iterrows():
    path = Path(dataset["fastq_file"])
    if not path.is_file():
        raise FileNotFoundError(path)

    records = list(SeqIO.parse(str(path), "fastq"))

    if len(records) != len(original_records):
        raise ValueError(f"Record count mismatch: {path}")

    dataset_keys = [spot_key(r) for r in records]
    dataset_ids = [r.id for r in records]
    original_ids = [r.id for r in original_records]

    if dataset_keys != original_keys or dataset_ids != original_ids:
        raise ValueError(
            f"Record order or identifiers do not match original: {path}"
        )

# Deterministically order spots, then assign whole spots to partitions.
spot_keys = sorted(
    spot_positions,
    key=lambda key: hashlib.sha256(key.encode("utf-8")).hexdigest()
)

n_spots = len(spot_keys)
n_train = int(n_spots * 0.70)
n_validation = int(n_spots * 0.15)

spot_split = {}

for key in spot_keys[:n_train]:
    spot_split[key] = "train"

for key in spot_keys[n_train:n_train + n_validation]:
    spot_split[key] = "validation"

for key in spot_keys[n_train + n_validation:]:
    spot_split[key] = "test"

# Build the manifest for all seven classes.
rows = []
for _, dataset in manifest.iterrows():
    for index, record in enumerate(original_records):
        key = original_keys[index]
        rows.append({
            "fastq_file": dataset["fastq_file"],
            "label": dataset["label"],
            "read_id": record.id,
            "read_index": index,
            "spot_id": key,
            "split": spot_split[key]
        })

result = pd.DataFrame(rows)

# Ensure every sequencing spot belongs to exactly one partition.
if result.groupby("spot_id")["split"].nunique().max() != 1:
    raise ValueError("A sequencing spot appears in multiple splits.")

output_path.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(output_path, index=False)

print("All seven FASTQ files passed the order and identifier checks.")
print(f"Extracted records: {len(original_records):,}")
print(f"Unique sequencing spots: {n_spots:,}")
print(f"Classes: {manifest['label'].nunique()}")
print(f"Total labelled examples: {len(result):,}")
print(f"\nSaved split manifest: {output_path}")

print("\nRecords per split:")
print(result.groupby("split").size().reindex(
    ["train", "validation", "test"]
))

print("\nUnique spots per split:")
print(pd.Series(spot_split).value_counts().reindex(
    ["train", "validation", "test"]
))

print("\nExamples per class and split:")
print(result.groupby(["label", "split"]).size().unstack(fill_value=0))

print("\nRecords per sequencing spot (first few group sizes):")
print(Counter(len(pos) for pos in spot_positions.values()))
