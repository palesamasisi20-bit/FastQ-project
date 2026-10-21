from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch

MODEL_NAME = "InstaDeepAI/nucleotide-transformer-v2-50m-multi-species"

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

sequence = "ACGTACGTACGTACGTACGTACGTACGTACGT"

print("Tokenizing sequence...")
inputs = tokenizer(
    sequence,
    return_tensors="pt"
)

print("Running model...")
with torch.no_grad():
    outputs = model(
        **inputs,
        output_hidden_states=True
    )

hidden = outputs.hidden_states[-1]

print("Sequence:", sequence)
print("Tokenized shape:", inputs["input_ids"].shape)
print("Hidden-state shape:", hidden.shape)
print("Model hidden size:", model.config.hidden_size)
print("Test successful!")
