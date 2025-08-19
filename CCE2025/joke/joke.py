import time
from pwn import *
from Crypto.Util.number import bytes_to_long
from jokes import joke_list

def find_joke_by_bruteforce(N, e, ciphertext, jokes):
    for joke in jokes:
        m_int = bytes_to_long(joke.encode())
        c_candidate = pow(m_int, e, N)
        if c_candidate == ciphertext:
            return joke
            
    return None

HOST, PORT = '16.184.44.93', 18892

proc = remote(HOST, PORT)

try:
    for i in range(10):
        log.info(f"--- Stage {i+1}/10 Start ---")
        proc.recvuntil(b'N = ')
        N = int(proc.recvline().strip(), 16)
        proc.recvuntil(b'e = ')
        e = int(proc.recvline().strip(), 16)
        proc.recvuntil(b'Encrypted message: ')
        ciphertext = int(proc.recvline().strip(), 16)
        
        decrypted_message = find_joke_by_bruteforce(N, e, ciphertext, joke_list)

        if decrypted_message:
            log.success(f"Answer : {decrypted_message}")
            proc.recvuntil(b"Enter the decrypted message: ")
            proc.sendline(decrypted_message.encode())
            proc.recvline()
        else:
            log.failure("Fail")
            break
            
    print(proc.recvall(timeout=2).decode())

except Exception as e:
    log.error(f"Error : {e}")

finally:
    proc.close()