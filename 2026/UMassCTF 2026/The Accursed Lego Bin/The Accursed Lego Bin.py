import random


text = "I_LOVE_RNG"
plain_num = int.from_bytes(text.encode(), "big")
e = 7
real_seed = plain_num ** e 
enc_flag_hex = "a9fa3c5e51d4cea498554399848ad14aa0764e15a6a2110b6613f5dc87fa70f17fafbba7eb5a2a5179"

enc_flag_bytes = bytes.fromhex(enc_flag_hex)
shuffled_bits = []
for b in enc_flag_bytes:
    shuffled_bits.extend(list(bin(b)[2:].zfill(8)))
    
num_bits = len(shuffled_bits)
indices = list(range(num_bits))
for i in range(10):
    random.seed(real_seed * (i + 1))
    random.shuffle(indices)
original_bits = [''] * num_bits
for i, orig_idx in enumerate(indices):
    original_bits[orig_idx] = shuffled_bits[i]
flag = ""
for i in range(0, num_bits, 8):
    byte_str = "".join(original_bits[i:i+8])
    flag += chr(int(byte_str, 2))
print(f"Flag : {flag}")

