import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/alignment_summary.csv")

datasets = [
    "sars_50k_original",
    "sars_50k_substitution",
    "sars_50k_insertion",
    "sars_50k_deletion",
    "sars_50k_nmasking",
    "sars_50k_low_complexity",
    "sars_50k_adapter_insertion",
]

labels = {
    "sars_50k_original": "Original (clean)",
    "sars_50k_substitution": "Substitution",
    "sars_50k_insertion": "Insertion",
    "sars_50k_deletion": "Deletion",
    "sars_50k_nmasking": "N-masking",
    "sars_50k_low_complexity": "Low complexity",
    "sars_50k_adapter_insertion": "Adapter insertion",
}

df = df.set_index("dataset").loc[datasets].reset_index()

plt.figure(figsize=(11, 6))
bars = plt.bar(
    [labels[name] for name in df["dataset"]],
    df["mapping_rate"]
)

plt.ylabel("Reads mapped (%)")
plt.xlabel("Dataset")
plt.title("Alignment Mapping Rate Before and After Synthetic Corruption")
plt.ylim(0, 105)
plt.xticks(rotation=30, ha="right")

for bar, value in zip(bars, df["mapping_rate"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{value:.2f}%",
        ha="center",
        fontsize=9
    )

plt.tight_layout()
plt.savefig("results/alignment_before_after.png", dpi=300)
plt.close()

print("Plot saved to results/alignment_before_after.png")
