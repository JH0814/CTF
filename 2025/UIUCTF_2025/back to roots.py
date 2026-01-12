from decimal import Decimal, getcontext
from hashlib import md5
from Crypto.Cipher import AES


leak = 4336282047950153046404
ct = "7863c63a4bb2c782eb67f32928a1deceaee0259d096b192976615fba644558b2ef62e48740f7f28da587846a81697745"
ct = bytes.fromhex(ct)


leak_str = str(leak)
leak_dec = Decimal(leak) / (10**len(leak_str))

K = 0
for i in range(100000, 316228):
    tmp = Decimal(i) + leak_dec
    K_tmp = round(tmp * tmp)
    re_sqrt_k = Decimal(K_tmp).sqrt()
    re_leak_str = str(re_sqrt_k).split('.')[-1]
    if re_leak_str.startswith(leak_str):
        K = K_tmp
        print(f"K 찾음: {K}")
        break
if K != 0:
    key = md5(str(K).encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_flag = cipher.decrypt(ct)
    print(f"Flag: {decrypted_flag.decode(errors='ignore')}")