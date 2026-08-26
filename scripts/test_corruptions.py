from Bio import SeqIO

# ============================================================
# SETTINGS
# ============================================================

ORIGINAL_FASTQ = "data/sars_50k.fastq"

CORRUPTED_FILES = {
    "substitution": "data/sars_50k_substitution.fastq",
    "deletion": "data/sars_50k_deletion.fastq",
    "insertion": "data/sars_50k_insertion.fastq",
    "N-masking": "data/sars_50k_nmasking.fastq",
    "low-complexity": "data/sars_50k_low_complexity.fastq",
    "adapter insertion": "data/sars_50k_adapter_insertion.fastq",
}


# ============================================================
# LOAD ORIGINAL READS
# ============================================================

original_reads = list(SeqIO.parse(ORIGINAL_FASTQ, "fastq"))

print("=" * 70)
print("DeepFASTQ Corruption Validation")
print("=" * 70)

print(f"Original reads: {len(original_reads)}")


# ============================================================
# FUNCTION TO TEST ONE CORRUPTION
# ============================================================

def test_corruption(name, corrupted_file):

    corrupted_reads = list(SeqIO.parse(corrupted_file, "fastq"))

    print("\n" + "-" * 70)
    print(f"CORRUPTION: {name}")
    print("-" * 70)

    print(f"Original reads : {len(original_reads)}")
    print(f"Corrupted reads: {len(corrupted_reads)}")

    if len(original_reads) != len(corrupted_reads):
        print("WARNING: Number of reads does not match!")
        return

    reads_changed = 0
    reads_same_length = 0
    reads_longer = 0
    reads_shorter = 0

    total_substitutions = 0
    total_inserted_bases = 0
    total_deleted_bases = 0
    total_N_bases = 0

    # --------------------------------------------------------
    # Compare every original read with corrupted read
    # --------------------------------------------------------

    for original, corrupted in zip(original_reads, corrupted_reads):

        original_seq = str(original.seq)
        corrupted_seq = str(corrupted.seq)

        original_length = len(original_seq)
        corrupted_length = len(corrupted_seq)

        # Check whether read changed
        if original_seq != corrupted_seq:
            reads_changed += 1

        # Length comparison
        if corrupted_length == original_length:
            reads_same_length += 1

        elif corrupted_length > original_length:
            reads_longer += 1
            total_inserted_bases += corrupted_length - original_length

        elif corrupted_length < original_length:
            reads_shorter += 1
            total_deleted_bases += original_length - corrupted_length

        # ----------------------------------------------------
        # N-masking
        # ----------------------------------------------------

        if name == "N-masking":
            total_N_bases += corrupted_seq.count("N")

        # ----------------------------------------------------
        # Substitution
        # ----------------------------------------------------

        if name == "substitution":

            # Substitution does NOT change read length.
            # Compare bases at the same positions.

            for a, b in zip(original_seq, corrupted_seq):

                if a != b:
                    total_substitutions += 1


    # ========================================================
    # RESULTS
    # ========================================================

    print(f"Reads changed       : {reads_changed}")
    print(f"Reads unchanged     : {len(original_reads) - reads_changed}")

    print(f"Reads same length   : {reads_same_length}")
    print(f"Reads longer        : {reads_longer}")
    print(f"Reads shorter       : {reads_shorter}")

    # --------------------------------------------------------
    # Substitution results
    # --------------------------------------------------------

    if name == "substitution":

        print()
        print(f"Total substituted bases: {total_substitutions}")

        print(
            f"Average substitutions/read: "
            f"{total_substitutions / len(original_reads):.2f}"
        )

        print("Expected: read length should remain unchanged.")

    # --------------------------------------------------------
    # Insertion results
    # --------------------------------------------------------

    elif name == "insertion":

        print()
        print(f"Total inserted bases: {total_inserted_bases}")

        print(
            f"Average inserted bases/read: "
            f"{total_inserted_bases / len(original_reads):.2f}"
        )

        print("Expected: corrupted reads should be longer.")

    # --------------------------------------------------------
    # Deletion results
    # --------------------------------------------------------

    elif name == "deletion":

        print()
        print(f"Total deleted bases: {total_deleted_bases}")

        print(
            f"Average deleted bases/read: "
            f"{total_deleted_bases / len(original_reads):.2f}"
        )

        print("Expected: corrupted reads should be shorter.")

    # --------------------------------------------------------
    # N-masking results
    # --------------------------------------------------------

    elif name == "N-masking":

        print()
        print(f"Total N bases: {total_N_bases}")

        print(
            f"Average N bases/read: "
            f"{total_N_bases / len(original_reads):.2f}"
        )

        print("Expected: read length should remain unchanged.")

    # --------------------------------------------------------
    # Adapter insertion
    # --------------------------------------------------------

    elif name == "adapter insertion":

        print()
        print(f"Total inserted bases: {total_inserted_bases}")

        print(
            f"Average inserted bases/read: "
            f"{total_inserted_bases / len(original_reads):.2f}"
        )

        print("Expected: corrupted reads should be longer.")

    # --------------------------------------------------------
    # Low-complexity injection
    # --------------------------------------------------------

    elif name == "low-complexity":

        print()
        print(f"Total inserted bases: {total_inserted_bases}")

        print(
            f"Average inserted bases/read: "
            f"{total_inserted_bases / len(original_reads):.2f}"
        )

        print(
            "Expected: reads should be longer if "
            "low-complexity sequence was inserted."
        )


# ============================================================
# RUN ALL TESTS
# ============================================================

for corruption_name, corrupted_file in CORRUPTED_FILES.items():

    try:
        test_corruption(corruption_name, corrupted_file)

    except FileNotFoundError:
        print("\n" + "-" * 70)
        print(f"SKIPPED: {corruption_name}")
        print(f"File not found: {corrupted_file}")
        print("-" * 70)


# ============================================================
# FINISHED
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)