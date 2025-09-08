final_flag = [0x94, 0x7, 0xd4, 0x64, 0x7, 0x54, 0x63, 0x24, 0xad, 0x98, 0x45, 0x72, 0x35]

def inv_inc(byte_val):
    return (byte_val - 1) & 0xFF
def inv_eor(byte_val):
    return byte_val ^ 0x69
def inv_rtr(byte_val):
    return ((byte_val << 1) | (byte_val >> 7)) & 0xFF
def inv_off(byte_val):
    return (byte_val - 15) & 0xFF

val = final_flag[0]
val = inv_rtr(val)
val = inv_eor(val)
val = inv_off(val)
char1 = val

val = final_flag[1]
val = inv_eor(val)
char2 = val

val = final_flag[2]
val = inv_rtr(val)
val = inv_off(val)
val = inv_rtr(val)
char3 = val

val = final_flag[3]
val = inv_eor(val)
val = inv_rtr(val)
val = inv_rtr(val)
char4 = val

val = final_flag[4]
val = inv_eor(val)
char5 = val

val = final_flag[5]
val = inv_rtr(val)
val = inv_off(val)
val = inv_rtr(val)
char6 = val

val = final_flag[6]
val = inv_rtr(val)
val = inv_eor(val)
val = inv_rtr(val)
char7 = val

val = final_flag[7]
val = inv_eor(val)
val = inv_rtr(val)
val = inv_rtr(val)
char8 = val

val = final_flag[8]
val = inv_eor(val)
val = inv_off(val)
val = inv_rtr(val)
char9 = val

val = final_flag[9]
val = inv_rtr(val)
char10 = val

val = final_flag[10]
val = inv_rtr(val)
val = inv_off(val)
val = inv_off(val)
char11 = val

val = final_flag[11]
val = inv_eor(val)
val = inv_rtr(val)
val = inv_rtr(val)
char12 = val

val = final_flag[12]
val = inv_rtr(val)
val = inv_off(val)
val = inv_eor(val)
char13 = val

flag_bytes = [
    char1, char2, char3, char4, char5, char6, char7,
    char8, char9, char10, char11, char12, char13
]

flag = "".join(map(chr, flag_bytes))

print("Flag : ictf{" + flag + "}")