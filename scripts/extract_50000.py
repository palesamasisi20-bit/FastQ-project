from Bio import SeqIO

input_file = "data/SRR39046143.fastq"
output_file = "data/sars_50k.fastq"

count = 0

with open(output_file, "w") as out_handle:

    for record in SeqIO.parse(input_file, "fastq"):

        SeqIO.write(record, out_handle, "fastq")

        count += 1

        if count == 50000:
            break

print("Saved", count, "reads")

