from pwn import *
from functools import partial
import re
import random

random.seed(121728)
p = remote("streams.tamuctf.com", 443, ssl=True, sni="random-password")

N = 0
while True:
    num = random.random()
    if num == 0.9992610559813815:
        break
    N += 1
N += 1
random.seed(121728)
rand_vals = [random.random() for _ in range(N)]

jump_0 = [-1] *N
jump_1 = [-1] * N

for i in range(N):
    cur_sum = 0
    j = i
    while j < N and cur_sum < 5:
        cur_sum += rand_vals[j]
        j += 1
    if cur_sum >= 5:
        jump_0[i] = j
    cur_sum = 0
    j = i
    while j < N and cur_sum < 17:
        cur_sum += rand_vals[j]
        j += 1
    if cur_sum >= 17:
        jump_1[i] = j


import sys
sys.setrecursionlimit(2000)
visited = set()
password_bits = []
def dfs(bit_count, cur_idx):
    if cur_idx == -1:
        return False
    if bit_count == 256:
        if cur_idx == N:
            return True
        return False
    state = (bit_count, cur_idx)
    if state in visited:
        return False
    visited.add(state)
    if dfs(bit_count + 1, jump_0[cur_idx]):
        password_bits.append('0')
        return True
    if dfs(bit_count + 1, jump_1[cur_idx]):
        password_bits.append('1')
        return True
    return False
if dfs(0, 0):
    password_bits.reverse()
    bin_str = "".join(password_bits)
    ans = hex(int(bin_str, 2))[2:].zfill(64)
    log.success(f"Password : {ans}")
    p.sendlineafter(b"hex: ", str(ans).encode())
    p.interactive()
