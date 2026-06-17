# DeepFASTQ Project

## Objective

Investigate whether genomic language models can detect sequencing artefacts in FASTQ reads.

## Dataset

- Organism: SARS-CoV-2
- SRA accession: SRR39046143
- Platform: Illumina
- Total reads: ~487,928
- Working subset: 50,000 reads

## Current Progress

- Downloaded FASTQ data from SRA
- Extracted 50,000 reads
- Implemented synthetic corruption methods:
  - Substitutions
  - Insertions
  - Deletions
- Generated corrupted FASTQ dataset
- Verified corruption pipeline

## Scripts

- extract_50000.py
- corrupt_fastq.py
- generate_corrupted_fastq.py
- check_corruptions.py

## Next Steps

- Alignment-based analysis using BWA
- Generate labels
- Feature extraction
- Machine learning evaluation