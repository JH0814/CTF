import sys
from hashlib import sha256
from itertools import product

V = [14, 38, 56, 76, 51]
C = [1357, 2854, 1102, 1723, 4416, 283, 344, 4566, 5023, 1798, 477, 3833, 1839, 5416, 4017, 1066, 161, 415, 5637, 1696, 1058, 3025, 5286, 5141, 3818, 1373, 2839, 1102, 1764, 4432, 313, 322, 4545, 5012, 1835, 477, 3825]
TARGET_HASH = "e256693b7b7d07e11f2f83f452f04969ea327261d56406d2d657da1066cefa17"

def is_flag_char(n):
    if 48 <= n <= 57 or 65 <= n <= 90 or 97 <= n <= 122 or n == 95 or n == 123 or n == 125:
        return True
    return False

key_matrix = [[[] for _ in range(5)] for _ in range(5)]

for row in range(5):
    for col in range(5):
        v = V[col]
        key_idx = row * 5 + col
        c_values = C[key_idx::25]
        if not c_values:
            key_matrix[row][col].append(0)
            continue
        for r in range(101):
            k = v * r
            check = True
            for c in c_values:
                if not is_flag_char(c ^ k):
                    check = False
                    break
            if check:
                key_matrix[row][col].append(k)
        if not key_matrix[row][col]:
             sys.exit(1)

key_list = []
for row in range(5):
    for col in range(5):
        key_list.append(key_matrix[row][col])

flag = ""
for key_tuple in product(*key_list):
    key = [[0] * 5 for _ in range(5)]
    for i in range(25):
        key[i // 5][i % 5] = key_tuple[i]
    
    flag_cand = ""
    for i in range(len(C)):
        row = (i // 5) % 5
        col = i % 5
        k = key[row][col]
        flag_cand += chr(C[i] ^ k)

    flag_hash = sha256(flag_cand.encode()).digest().hex()

    if flag_hash == TARGET_HASH:
        flag = flag_cand
        break

if flag:
    print(f"Flag : {flag}")