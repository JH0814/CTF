from pwn import *
from randcrack import RandCrack
import hashlib
import hmac
import re

# p = process(["python3", "chall.py"])
p = remote('34.162.20.138', 5000)
rc = RandCrack()

def get_predicted_roll(server_seed, client_seed, nonce):
    nonce_client_msg = f"{client_seed}-{nonce}".encode()
    sig = hmac.new(str(server_seed).encode(), nonce_client_msg, hashlib.sha256).hexdigest()
    index = 0
    lucky = int(sig[index*5:index*5+5], 16)
    while (lucky >= 1e6):
        index += 1
        lucky = int(sig[index * 5:index * 5 + 5], 16)
        if (index * 5 + 5 > 129):
            lucky = 9999
            break
    return round((lucky % 1e4) * 1e-2)


p.sendlineafter(b"> ", b"b")
p.sendlineafter(b"1.0): ", b"1")
p.sendlineafter(b"(int): ", b"624") 
p.sendlineafter(b"2-98 ", b"90")
p.sendlineafter(b"(Y/N)", b"Y")

for _ in range(624):
    p.recvuntil(b"Server-Seed: ")
    seed = p.recvline().strip().decode()
    rc.submit(int(re.search(r"(\d+)", seed).group(1)))

p.recvuntil(b"Final Balance: ")
balance = float(p.recvline().strip())
p.recvuntil(b"> ")

nonce = 624
client_seed = "1337awesome"

while balance < 10000:
    pred_seed = rc.predict_getrandbits(32)
    roll = get_predicted_roll(pred_seed, client_seed, nonce)
    
    p.sendline(b"b") 
    
    prompt = p.recvuntil(b": ").decode()
    min_wager = 1.0
    match = re.search(r"min-wager is ([\d\.]+)", prompt)
    if match:
        min_wager = float(match.group(1))
    
    greed = max(2, int(roll))
    wager = min_wager if greed > 95 else balance
    if wager < min_wager: 
        wager = min_wager

    p.sendline(str(wager).encode()) 
    p.sendlineafter(b"(int): ", b"1") 
    p.sendlineafter(b"between 2-98 ", str(greed).encode())
    p.sendlineafter(b"(Y/N)", b"Y")

    p.recvuntil(b"Final Balance: ")
    balance = float(p.recvline().strip())
    p.recvuntil(b"> ")
    
    nonce += 1

p.sendline(b"a")
p.sendlineafter(b"> ", b"a")
p.interactive()