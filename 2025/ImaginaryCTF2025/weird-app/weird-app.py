enc = "idvi+1{s6e3{)arg2zv[moqa905+"

def decrypt_flag(enc):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"
    symbols = "!@#$%^&*()_+{}[]|"
    ans = ""
    for i, c in enumerate(enc):
        if c in alphabet:
            enc_idx = alphabet.find(c)
            orig_idx = (enc_idx - i + len(alphabet)) % len(alphabet)
            ans += alphabet[orig_idx]
        elif c in digits:
            enc_idx = digits.find(c)
            orig_idx = (enc_idx - (i * 2) + len(digits)) % len(digits)
            ans += digits[orig_idx]
        elif c in symbols:
            enc_idx = symbols.find(c)
            orig_idx = (enc_idx - (i * i) + len(symbols)) % len(symbols)
            ans += symbols[orig_idx]
        else:
            ans += c
    return ans

print("Flag : ", decrypt_flag(enc))