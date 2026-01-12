from pwn import *

HOST, PORT = "chall.polygl0ts.ch", 6001

context.log_level = 'error'
flag = ""

print("Start...")

for _ in range(32):
    for i in range(10):
        p = remote(HOST, PORT)
        
        p.sendlineafter(b"Don't even think to guess the flag by brute force, it is 32 digits long!\n", (flag + str(i)).encode())
        
        if b"Correct" in p.recvall():
            flag += str(i)
            print(f"Found: {flag}")
            p.close()
            break
        
        p.close()

print(f"Result: EPFL{{{flag}}}")