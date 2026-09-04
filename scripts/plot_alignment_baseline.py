import pandas as pd
import matplotlib.pyplot as plt

input_file = "results/alignment_baseline.csv"
output_file = "results/alignment_baseline_comparison.png"

df = pd.read_csv(input_file)

# Remove the original and generic corrupted datasets from this plot
df_plot = df[
    (df["dataset"] != "sars_50k_original") &
    (df["dataset"] != "sars_50k_corrupted")
].copy()

# Clean dataset names for the x-axis
df_plot["dataset"] = df_plot["dataset"].str.replace(
    "sars_50k_", "", regex=False
)

x = range(len(df_plot))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 7))

ax.bar(
    [i - width / 2 for i in x],
    df_plot["mapping_rate_drop_pp"],
    width,
    label="Mapping-rate drop"
)

ax.bar(
    [i + width / 2 for i in x],
    df_plot["error_rate_increase_pp"],
    width,
    label="Error-rate increase"
)

ax.set_xlabel("Corruption type")
ax.set_ylabel("Change (percentage points)")
ax.set_title("Alignment Impact of FASTQ Corruptions")
ax.set_xticks(list(x))
ax.set_xticklabels(
    df_plot["dataset"],
    rotation=35,
    ha="right"
)

ax.legend()

plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.close()

print(f"Created {output_file}")
