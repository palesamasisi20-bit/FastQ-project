from Bio import SeqIO
from Bio.Seq import Seq
import random


def substitute_base(sequence):

    bases = ["A", "T", "G", "C"]

    sequence = list(sequence)

    position = random.randint(0, len(sequence)-1)

    original = sequence[position]

    choices = [b for b in bases if b != original]

    sequence[position] = random.choice(choices)

    return "".join(sequence)


input_file = "data/sars_50k.fastq"

output_file = "data/sars_50k_corrupted.fastq"

count = 0


with open(output_file, "w") as output_handle:

    for record in SeqIO.parse(input_file, "fastq"):

        original = str(record.seq)

        corrupted = substitute_base(original)

        record.seq = Seq(corrupted)

        SeqIO.write(record, output_handle, "fastq")

        count += 1


print("Finished!")
print("Reads processed:", count)