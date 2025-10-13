import binascii
import string

expected = [
    2508312701, 1231198871, 1473663577, 1022026391, 4277043751, 1684325040
]

found_inputs = []

for target in expected:
    found = False
    if target == 1473663577:
        charset = string.ascii_lowercase
    else:
        charset = string.ascii_letters + string.digits + string.punctuation
    
    for length in range(1, 9):
        if found:
            break
        def generate_strings(prefix):
            global found
            if found:
                return
            if len(prefix) == length:
                data = prefix.encode('utf-8')
                calculated_crc = binascii.crc32(data) & 0xFFFFFFFF
                if calculated_crc == target:
                    found_inputs.append(prefix)
                    found = True
                return
            for char in charset:
                generate_strings(prefix + char)
        generate_strings("")

flag = "FlagY{" + "_".join(found_inputs) + "}"
print(f"Flag : {flag}")