from Bio import SeqIO
import random


def substitute_base(sequence):

    bases = ["A", "T", "G", "C"]

    sequence = list(sequence)

    position = random.randint(0, len(sequence)-1)

    original = sequence[position]

    choices = [b for b in bases if b != original]

    sequence[position] = random.choice(choices)

    return "".join(sequence)


for record in SeqIO.parse("data/sars_50k.fastq", "fastq"):

    original = str(record.seq)

    corrupted = substitute_base(original)

    print("Read ID :", record.id)
    print("Length  :", len(original))

    print("\nOriginal:")
    print(original[:100])

    print("\nCorrupted:")
    print(corrupted[:100])

    break