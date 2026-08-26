from Bio import SeqIO
from Bio.Seq import Seq
import random


# ============================================================
# SETTINGS
# ============================================================

INPUT_FASTQ = "data/sars_50k.fastq"

# Change ONLY this line when moving to another corruption
CORRUPTION_TYPE = "adapter_insertion"

# Default corruption rate
RATE = 0.1

# Output file
OUTPUT_FASTQ = f"data/sars_50k_{CORRUPTION_TYPE}.fastq"


# ============================================================
# CORRUPTION FUNCTIONS
# ============================================================

def substitute_bases(sequence, rate):
    """
    Randomly substitute bases.
    Read length stays the same.
    """
    bases = ["A", "T", "G", "C"]
    sequence = list(sequence)

    changed = 0

    for i in range(len(sequence)):
        if random.random() < rate:
            original = sequence[i]
            choices = [b for b in bases if b != original]

            sequence[i] = random.choice(choices)
            changed += 1

    return "".join(sequence), changed


def delete_bases(sequence, rate):
    """
    Randomly delete bases.
    Read length becomes shorter.
    """
    sequence = list(sequence)

    keep = []
    deleted = 0

    for base in sequence:
        if random.random() < rate:
            deleted += 1
        else:
            keep.append(base)

    # Make sure at least one base remains
    if len(keep) == 0:
        keep.append(sequence[0])
        deleted -= 1

    return "".join(keep), deleted


def insert_bases(sequence, rate):
    """
    Insert random bases into the read.
    """
    bases = ["A", "T", "G", "C"]

    sequence = list(sequence)

    inserted = 0

    # Number of bases to insert
    number_to_insert = max(1, int(len(sequence) * rate))

    for _ in range(number_to_insert):
        position = random.randint(0, len(sequence))
        base = random.choice(bases)

        sequence.insert(position, base)
        inserted += 1

    return "".join(sequence), inserted


def n_mask(sequence, rate):
    """
    Replace bases with N.
    Read length stays the same.
    """
    sequence = list(sequence)

    changed = 0

    for i in range(len(sequence)):
        if random.random() < rate:
            if sequence[i] != "N":
                sequence[i] = "N"
                changed += 1

    return "".join(sequence), changed


def low_complexity_injection(sequence, rate):
    """
    Insert a low-complexity sequence into the read.
    Uses repeated bases such as AAAAAAAAAAAA.
    """
    sequence = list(sequence)

    number_to_insert = max(1, int(len(sequence) * rate))

    # Choose one base and repeat it
    base = random.choice(["A", "T", "G", "C"])

    low_complexity = [base] * number_to_insert

    position = random.randint(0, len(sequence))

    sequence[position:position] = low_complexity

    return "".join(sequence), number_to_insert


def adapter_insertion(sequence, rate):
    """
    Insert an Illumina adapter sequence into the read.

    A 12-base adapter fragment is used so that the
    synthetic corruption is moderate and comparable
    in size to the other insertion corruptions.
    """

    # Illumina adapter sequence
    adapter = "AGATCGGAAGAG"

    sequence = list(sequence)

    # Insert the adapter once per read
    position = random.randint(0, len(sequence))

    sequence[position:position] = list(adapter)

    return "".join(sequence), len(adapter)


# ============================================================
# PROCESS FASTQ
# ============================================================

count = 0
reads_changed = 0


with open(OUTPUT_FASTQ, "w") as output_handle:

    for record in SeqIO.parse(INPUT_FASTQ, "fastq"):

        original = str(record.seq)

        # Save original quality scores
        original_quality = record.letter_annotations["phred_quality"]

        # ----------------------------------------------------
        # APPLY SELECTED CORRUPTION
        # ----------------------------------------------------

        if CORRUPTION_TYPE == "substitution":

            corrupted, changed = substitute_bases(
                original,
                RATE
            )

            reads_changed += int(changed > 0)

            new_quality = original_quality[:len(corrupted)]


        elif CORRUPTION_TYPE == "deletion":

            corrupted, changed = delete_bases(
                original,
                RATE
            )

            reads_changed += int(changed > 0)

            new_quality = original_quality[:len(corrupted)]


        elif CORRUPTION_TYPE == "insertion":

            corrupted, changed = insert_bases(
                original,
                RATE
            )

            reads_changed += 1

            # Give inserted bases the quality of the
            # surrounding read position
            inserted_quality = [
                original_quality[min(len(original_quality) - 1,
                                      len(original_quality) // 2)]
            ] * changed

            midpoint = len(original_quality) // 2

            new_quality = (
                original_quality[:midpoint]
                + inserted_quality
                + original_quality[midpoint:]
            )


        elif CORRUPTION_TYPE == "N-masking":

            corrupted, changed = n_mask(
                original,
                RATE
            )

            reads_changed += int(changed > 0)

            new_quality = original_quality[:len(corrupted)]


        elif CORRUPTION_TYPE == "low-complexity":

            corrupted, changed = low_complexity_injection(
                original,
                RATE
            )

            reads_changed += 1

            inserted_quality = [
                original_quality[min(len(original_quality) - 1,
                                      len(original_quality) // 2)]
            ] * changed

            midpoint = len(original_quality) // 2

            new_quality = (
                original_quality[:midpoint]
                + inserted_quality
                + original_quality[midpoint:]
            )


        elif CORRUPTION_TYPE == "adapter_insertion":

            corrupted, changed = adapter_insertion(
                original,
                RATE
            )

            reads_changed += 1

            inserted_quality = [
                original_quality[min(len(original_quality) - 1,
                                      len(original_quality) // 2)]
            ] * changed

            midpoint = len(original_quality) // 2

            new_quality = (
                original_quality[:midpoint]
                + inserted_quality
                + original_quality[midpoint:]
            )


        else:

            raise ValueError(
                "Unknown corruption type: "
                + CORRUPTION_TYPE
            )


        # ----------------------------------------------------
        # UPDATE FASTQ RECORD
        # ----------------------------------------------------

        record.letter_annotations.clear()

        record.seq = Seq(corrupted)

        record.letter_annotations["phred_quality"] = new_quality[:len(corrupted)]

        SeqIO.write(
            record,
            output_handle,
            "fastq"
        )

        count += 1


# ============================================================
# SUMMARY
# ============================================================

print("Finished!")
print("Reads processed:", count)
print("Reads changed:", reads_changed)
print("Corruption type:", CORRUPTION_TYPE)
print("Rate:", RATE)
print("Output:", OUTPUT_FASTQ)