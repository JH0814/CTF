data_blob = open('./baby-goes-re', 'rb').read()

DATA_BASE = 0xcb6d5

acc1 = 0
acc2 = 0

flag = []
flag_length = 53
base_offset = 0x1337
step1_add = 0x1338
step2_add = 0x33

for i in range(flag_length):
    offset = acc1 + acc2 + base_offset + DATA_BASE
    if offset >= len(data_blob):
        break
    char_code = data_blob[offset]
    flag.append(chr(char_code))
    acc1_old = acc1
    acc2_old = acc2
    acc1 = acc1_old + acc2_old + step1_add
    acc2 = acc2_old + step2_add

if len(flag) == flag_length:
    print("Found correct flag:")
    print("".join(flag))
else:
    print("Fail")