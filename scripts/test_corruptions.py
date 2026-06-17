import random

def substitute_base(sequence):

    bases = ["A", "T", "G", "C"]

    sequence = list(sequence)

    position = random.randint(0, len(sequence)-1)

    original = sequence[position]

    choices = [b for b in bases if b != original]

    sequence[position] = random.choice(choices)

    return "".join(sequence)


test_read = "ATGCGTACGTAG"

corrupted = substitute_base(test_read)

print("Original :", test_read)
print("Corrupted:", corrupted)

def insert_base(sequence):

    bases = ["A", "T", "G", "C"]

    position = random.randint(0, len(sequence))

    new_base = random.choice(bases)

    sequence = list(sequence)

    sequence.insert(position, new_base)

    return "".join(sequence)
test_read = "ATGCGTACGTAG"

print("Original    :", test_read)
print("Insertion   :", insert_base(test_read))
def delete_base(sequence):

    sequence = list(sequence)

    position = random.randint(0, len(sequence)-1)

    sequence.pop(position)

    return "".join(sequence)
print("Deletion    :", delete_base(test_read))
test_read = "ATGCGTACGTAG"

deleted = delete_base(test_read)

print("Original :", test_read)
print("Length   :", len(test_read))

print("Deleted  :", deleted)
print("Length   :", len(deleted))