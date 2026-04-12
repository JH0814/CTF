expected = bytes.fromhex("3B54751A2406AF05778047C5E483D348CB8730DE1A9145AB15C79B2204022BEE")
flag_enc = bytes.fromhex("6E193449777DF05A07B433A68CE6E617FBE96FAE2EE526C370E3C47D277F2B00")

flag = bytearray()
for i in range(32):
    flag.append(expected[i] ^ flag_enc[i])

print(flag.decode('utf-8', errors='ignore'))