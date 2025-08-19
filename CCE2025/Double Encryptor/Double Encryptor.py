from Crypto.Cipher import AES, ARC4
import binascii

aes_key_hex = '2B7E151628AED2A6ABF7158809CF4F3C762E7E151628AED2A6ABF7158809CF4F'
rc4_key_hex = '8F1BC347D29A6E550FA834217CE912BD'

encrypted_data_hex = '21517927fe130833b4397f95854cb89681df1771b96726437163a9323e7b47f4fedf4355b2f17aa18ed0573f1ee7264302b6891a76565394e3a214f3c3d404ede3f11fb85f1e60c09fef50792c4efd99'

aes_key = binascii.unhexlify(aes_key_hex)
rc4_key = binascii.unhexlify(rc4_key_hex)
encrypted_data = binascii.unhexlify(encrypted_data_hex)

def unpad_pkcs7(data):
    padding_len = data[-1]
    if padding_len > len(data) or padding_len == 0:
        return data
    if data[-padding_len:] != bytes([padding_len]) * padding_len:
        return data
    return data[:-padding_len]

cipher_aes = AES.new(aes_key, AES.MODE_ECB)
aes_decrypted = cipher_aes.decrypt(encrypted_data)

unpadded_data = unpad_pkcs7(aes_decrypted)

cipher_rc4 = ARC4.new(rc4_key)
final_plaintext = cipher_rc4.decrypt(unpadded_data)

print(f"plaintext(hex): {final_plaintext.hex()}")
decoded_text = final_plaintext.decode('utf-8', errors='ignore')
print(f"plaintext(string): {decoded_text}")
    
