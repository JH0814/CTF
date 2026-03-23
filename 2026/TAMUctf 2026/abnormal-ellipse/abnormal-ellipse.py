from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib

secret_x = 46862424626771023060842312162194505004189661568357160582950231202292115713415

enc_data = bytes.fromhex("e31e0e638110d1e5c39764af90ac6194c1f9eaabd396703371dc2e6bb2932a18d824d86175ab071943cba7c093ccc6c6")
iv = bytes.fromhex("478876e42be078dceb3aee3a6a8f260f")

key = hashlib.sha256(secret_x.to_bytes((secret_x.bit_length() + 7) // 8, 'big')).digest()
cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
decryptor = cipher.decryptor()

padded_flag = decryptor.update(enc_data) + decryptor.finalize()

unpadder = padding.PKCS7(128).unpadder()
flag = unpadder.update(padded_flag) + unpadder.finalize()
print(f"Flag : {flag.decode('utf-8')}")
