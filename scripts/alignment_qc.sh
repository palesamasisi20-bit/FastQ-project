#!/bin/bash

REFERENCE="reference/NC_045512.2.fasta"
DATA="data"
RESULTS="results"

mkdir -p "$RESULTS"

for FASTQ in "$DATA"/sars_50k_*.fastq
do
    NAME=$(basename "$FASTQ" .fastq)

    echo "========================================"
    echo "Aligning: $NAME"
    echo "========================================"

    bwa mem "$REFERENCE" "$FASTQ" > "$RESULTS/${NAME}.sam"

    samtools view -bS "$RESULTS/${NAME}.sam" > "$RESULTS/${NAME}.bam"

    samtools sort "$RESULTS/${NAME}.bam" \
        -o "$RESULTS/${NAME}.sorted.bam"

    samtools index "$RESULTS/${NAME}.sorted.bam"

    samtools flagstat "$RESULTS/${NAME}.sorted.bam" \
        > "$RESULTS/${NAME}.flagstat.txt"

    echo "Finished: $NAME"
    echo
done

echo "All alignments completed."
