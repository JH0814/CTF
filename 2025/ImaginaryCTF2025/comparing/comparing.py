output_data = [
    "9548128459",
    "491095",
    "1014813",
    "561097",
    "10211614611201",
    "5748108475",
    "1171123",
    "516484615",
    "114959",
    "649969946",
    "1051160611501",
    "991021",
    "1231012101321",
    "9912515",
    "11411511",
    "1151164611511",
]

def rev_even(a: str):
    length = len(a)
    idx = 0
    while idx < length // 2 and a[idx] == a[length - 1 - idx]:
        idx += 1
    middle_part = a[idx : length - idx]
    vals_str = a[:idx]
    if not middle_part or not vals_str:
        return None
    try:
        ii = int(middle_part)
        if ii >= 16:
            return None
        for val1_len in [3, 2]:
            if len(vals_str) > val1_len:
                val1 = int(vals_str[:val1_len])
                val3 = int(vals_str[val1_len:])
                if len(str(val1)) + len(str(val3)) == len(vals_str):
                    if 32 <= val1 <= 126 and 32 <= val3 <= 126:
                        return val1, val3, ii
    except (ValueError, IndexError):
        return None
    return None

    

def rev_odd(a):
    if len(a) >= 6:
        try:
            ii = int(a[-2:])
            vals_str = a[:-2]
            for val1_len in [3, 2]:
                if len(vals_str) > val1_len:
                    val1 = int(vals_str[:val1_len])
                    val3 = int(vals_str[val1_len:])
                    if len(str(val1)) + len(str(val3)) == len(vals_str):
                        if ii < 16:
                            if 32 <= val1 <= 126 and 32 <= val3 <= 126:
                                return val1, val3, ii
        except (ValueError, IndexError):
            pass
    try:
        ii = int(a[-1:])
        vals_str = a[:-1]
        for val1_len in [3, 2]:
            if len(vals_str) > val1_len:
                val1 = int(vals_str[:val1_len])
                val3 = int(vals_str[val1_len:])
                if len(str(val1)) + len(str(val3)) == len(vals_str):
                    if ii < 16:
                        if 32 <= val1 <= 126 and 32 <= val3 <= 126:
                            return val1, val3, ii
    except (ValueError, IndexError):
        pass
    return None


ans_tuple = []
for i in range(0, len(output_data), 2):
    str1 = output_data[i]
    str2 = output_data[i+1]
    result1 = rev_even(str1)
    if result1 is None:
        result1 = rev_odd(str1)
    result2 = rev_even(str2)
    if result2 is None:
        result2 = rev_odd(str2)
    v1, v3, i1 = result1
    v2, v4, i2 = result2
    ans_tuple.append((chr(v1), chr(v2), i1))
    ans_tuple.append((chr(v3), chr(v4), i2))

ans_tuple.sort(key=lambda t: t[2])
flag_chars = []
for char1, char2, index in ans_tuple:
    flag_chars.append(char1)
    flag_chars.append(char2)

flag = "".join(flag_chars)

print("--- Flag ---")
print(flag)