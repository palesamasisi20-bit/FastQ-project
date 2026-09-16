import pandas as pd

datasets = [
    ("data/sars_50k.fastq", "original"),
    ("data/sars_50k_corrupted.fastq", "corrupted"),
    ("data/sars_50k_substitution.fastq", "substitution"),
    ("data/sars_50k_insertion.fastq", "insertion"),
    ("data/sars_50k_deletion.fastq", "deletion"),
    ("data/sars_50k_nmasking.fastq", "nmasking"),
    ("data/sars_50k_adapter_insertion.fastq", "adapter_insertion"),
    ("data/sars_50k_low_complexity.fastq", "low_complexity"),
]

df = pd.DataFrame(datasets, columns=["fastq_file", "label"])

df.to_csv("results/dataset_manifest.csv", index=False)

print("Created results/dataset_manifest.csv")
print(df.to_string(index=False))
