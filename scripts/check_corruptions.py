from Bio import SeqIO

original_file = "data/sars_50k.fastq"
corrupted_file = "data/sars_50k_corrupted.fastq"

total = 0
changed = 0

for original, corrupted in zip(
        SeqIO.parse(original_file, "fastq"),
        SeqIO.parse(corrupted_file, "fastq")):

    total += 1

    if str(original.seq) != str(corrupted.seq):
        changed += 1

print("Total reads   :", total)
print("Changed reads :", changed)