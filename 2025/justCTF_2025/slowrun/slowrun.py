from Crypto.Util.number import long_to_bytes
import sys

sys.setrecursionlimit(15000) 

F_cache = {}
G_cache = {}

F_cache[-1] = 1

def solve_G(m):
    if m in G_cache:
        return G_cache[m]
    if m <= 1:
        return 1
    res = (solve_F(m - 1) + 
           3 * solve_F(m - 2) - 
           5 * solve_F(m - 3) + 
           3 * (m**4))
            
    G_cache[m] = res
    return res

def solve_F(n):
    if n in F_cache:
        return F_cache[n]
    if n == 0:
        return 2
    if n == 1:
        return 1

    res = (73 * (n**5) + 
           8 * (n**3) + 
           n - 4 + 
           solve_G(n - 1))

    F_cache[n] = res
    return res

OFFSET_1 = 0x4008
OFFSET_2 = 0x40C0

def read_from_file(offset):
    with open('./slowrun', 'rb') as f:
        f.seek(offset)
        byte_list = []
        while True:
            byte = f.read(1)
            if not byte or byte == b'\x00':
                break
            byte_list.append(byte.decode('ascii'))
        return ''.join(byte_list)

c1 = int(read_from_file(OFFSET_1))
c2 = int(read_from_file(OFFSET_2))

input_n = 13337

X = solve_F(input_n)

flag_value = (X % c1) + c2

flag = long_to_bytes(flag_value).decode('ascii')
print(f"Flag: {flag}")