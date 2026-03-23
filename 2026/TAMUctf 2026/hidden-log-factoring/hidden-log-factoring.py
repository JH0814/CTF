import math
import random
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from Crypto.Util.number import long_to_bytes, bytes_to_long
from sympy.ntheory.residue_ntheory import nthroot_mod
from sympy.ntheory.modular import crt

n=71016310005824589926747341243598522145452505235842335510488353587223142066921470760443852767377534776713566052988373656012584808377496091765373981120165220471527586994259252074709653090148780742972203779666231432769553199154214563039426087870098774883375566546770723222752131892953195949848583409407713489831
e=65537

p=200167626629249973590210748210664315551571227173732968065685194568612605520816305417784745648399324178485097581867501503778073506528170960879344249321872139638179291829086442429009723480288604047975360660822750743411854623254328369265079475034447044479229192540942687284442586906047953374527204596869578972378578818243592790149118451253249
g=11
A=44209577951808382329528773174800640982676772266062718570752782238450958062000992024007390942331777802579750741643234627722057238001117859851305258592175283446986950906322475842276682130684406699583969531658154117541036033175624316123630171940523312498410797292015306505441358652764718889371372744612329404629522344917215516711582956706994

D=9478993126102369804166465392238441359765254122557022102787395039760473484373917895152043164556897759129379257347258713397227019255397523784552330568551257950882564054224108445256766524125007082113207841784651721510041313068567959041923601780557243220011462176445589034556139643023098611601440872439110251624
c=1479919887254219636530919475050983663848182436330538045427636138917562865693442211774911655964940989306960131568709021476461747472930022641984797332621318327273825157712858569934666380955735263664889604798016194035704361047493027641699022507373990773216443687431071760958198437503246519811635672063448591496


s = 485391067385099231898174017598 # SageMath로 구한 s 값을 여기에 넣으세요! 

if s == 0:
    print("[-] s 값을 먼저 구해서 입력해주세요.")
    exit()

print(f"[+] Found s: {s}")

def hkdf_mask(secret: bytes, length: int) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=b"rsa-d-mask",
        backend=default_backend()
    )
    return hkdf.derive(secret)

d_length = n.bit_length() // 8
mask = bytes_to_long(hkdf_mask(long_to_bytes(s), d_length))
d = D ^ mask
print(f"[+] Recovered d!")

def factor_rsa_n(n, e, d):
    k = e * d - 1
    t = k
    r = 0
    while t % 2 == 0:
        r += 1
        t //= 2
        
    while True:
        g_rand = random.randint(2, n - 1)
        x = pow(g_rand, t, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x_next = pow(x, 2, n)
            if x_next == 1:
                p_cand = math.gcd(x - 1, n)
                return p_cand, n // p_cand
            x = x_next
            if x == n - 1:
                break
        else:
            p_cand = math.gcd(x - 1, n)
            if 1 < p_cand < n:
                return p_cand, n // p_cand

print("[*] n 소인수분해 진행 중...")
q1, q2 = factor_rsa_n(n, e, d)
print(f"[+] Factored n into q1, q2!")

print("[*] Rabin 암호 복호화 진행 중...")
m1_roots = nthroot_mod(c, 2, q1, all_roots=True)
m2_roots = nthroot_mod(c, 2, q2, all_roots=True)

for r1 in m1_roots:
    for r2 in m2_roots:
        m, _ = crt([q1, q2], [r1, r2])
        
        pt_bytes = long_to_bytes(int(m))
        
        if (b'{' in pt_bytes or b'flag' in pt_bytes.lower()) and b"gigem{" in pt_bytes:
            print(f"FLAG FOUND (Raw Bytes): {pt_bytes}")
            print(f"FLAG FOUND (Text): {pt_bytes.decode('utf-8', errors='ignore')}")