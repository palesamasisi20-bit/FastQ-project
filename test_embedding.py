from Bio import SeqIO
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch

MODEL_NAME = "InstaDeepAI/nucleotide-transformer-v2-50m-multi-species"
FASTQ_FILE = "data/sars_50k.fastq"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

print("Loading model...")
model = AutoModelForMaskedLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model.eval()

# Read the first FASTQ read
record = next(SeqIO.parse(FASTQ_FILE, "fastq"))
sequence = str(record.seq)

print("Read ID:", record.id)
print("Read length:", len(sequence))
print("Sequence:", sequence[:100], "...")

# Tokenize the read
inputs = tokenizer(
    sequence,
    return_tensors="pt"
)

print("Tokenized shape:", inputs["input_ids"].shape)

# Run the model
print("Running model...")

with torch.no_grad():
    outputs = model(
        **inputs,
        output_hidden_states=True
    )

# Last hidden layer
hidden = outputs.hidden_states[-1]

print("Hidden-state shape:", hidden.shape)

# Mean pooling using the attention mask
attention_mask = inputs["attention_mask"].unsqueeze(-1)

masked_hidden = hidden * attention_mask

embedding = masked_hidden.sum(dim=1) / attention_mask.sum(dim=1)

print("Embedding shape:", embedding.shape)
print("Embedding dimension:", embedding.shape[-1])
print("First 10 values:", embedding[0, :10])

print("Embedding test successful!")
