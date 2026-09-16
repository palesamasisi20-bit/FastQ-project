import hashlib
import pandas as pd
from Bio import SeqIO

manifest_file = "results/dataset_manifest.csv"
output_file = "results/ml_dataset_manifest.csv"

manifest = pd.read_csv(manifest_file)

# Use the original reads to define the common split
original_file = "data/sars_50k.fastq"

records = []

for index, record in enumerate(SeqIO.parse(original_file, "fastq")):
    read_id = record.id

    # Deterministic assignment based on read ID
    hash_value = int(
        hashlib.md5(read_id.encode("utf-8")).hexdigest(),
        16
    )

    split = "test" if hash_value % 5 == 0 else "train"

    records.append({
        "read_id": read_id,
        "read_index": index,
        "split": split
    })

split_df = pd.DataFrame(records)

# Add every dataset to the same split
rows = []

for _, dataset in manifest.iterrows():
    for _, read in split_df.iterrows():
        rows.append({
            "fastq_file": dataset["fastq_file"],
            "label": dataset["label"],
            "read_id": read["read_id"],
            "read_index": read["read_index"],
            "split": read["split"]
        })

ml_df = pd.DataFrame(rows)

ml_df.to_csv(output_file, index=False)

print(f"Created {output_file}")
print(f"Total labelled reads: {len(ml_df)}")
print()
print("Reads per split:")
print(ml_df.groupby("split").size())
print()
print("Reads per class and split:")
print(ml_df.groupby(["label", "split"]).size())
