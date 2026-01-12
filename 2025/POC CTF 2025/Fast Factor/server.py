from Crypto.Util.number import bytes_to_long, getPrime
from os import urandom
import os

os.environ["FLAG1"] = "FAKE_FLAG"
os.environ["FLAG2"] = "FAKE_FLAG"

f1 = os.getenv("FLAG1", "FAKE_FLAG").encode()
f2 = os.getenv("FLAG2", "FAKE_FLAG").encode()
p,q,z = [getPrime(512) for _ in range(3)]
e = 0x10001
E = bytes_to_long(urandom(1337))
n1,n2 = p*q, q*z
c1,c2 = pow(bytes_to_long(f1),e,n1), pow(bytes_to_long(f2),e,n2)

print(f"n1 = {n1}\n")
print(f"c1 = {c1}\n")
print(f"c2 = {c2}\n")
print(f"x = {n1*E+n2}\n")