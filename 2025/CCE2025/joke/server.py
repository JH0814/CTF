from Crypto.Util.number import getPrime, GCD, bytes_to_long, long_to_bytes
from random import randint
from jokes import get_joke
from secret import flag

def rsa(nbits=1024, d_bits=256):
    p = getPrime(nbits // 2)
    q = getPrime(nbits // 2)

    N = p * q

    phi = (p - 1) * (q - 1)

    d_max = 2**d_bits
    while True:
        d = randint(2, d_max)
        if GCD(d, phi) == 1:
            break

    from Crypto.Util.number import inverse
    e = inverse(d, phi)

    return N, e, d

correct_count = 0

for i in range(10):
    print(f"\n=== Challenge {i+1}/10 ===")
    N, e, d = rsa()
    print("N =", hex(N))
    print("e =", hex(e))
    joke = get_joke()
    message_int = bytes_to_long(joke.encode())

    ciphertext = pow(message_int, e, N)
    print("Encrypted message:", hex(ciphertext))
    
    print("Can you decrypt this message?")
    user_input = input("Enter the decrypted message: ").strip()
    
    if user_input == joke:
        print("Correct!")
        correct_count += 1
    else:
        print("Wrong! The correct message was:", joke)
        break

if correct_count == 10:
    print(f"\n🎉 Congratulations! You solved all 10 challenges!")
    print(f"Here's your flag: {flag}")
else:
    print(f"\nYou got {correct_count}/10 correct. Try again!")