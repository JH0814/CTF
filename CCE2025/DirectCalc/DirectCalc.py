import base64

exp_table = [
    1, 2, 4, 8, 16, 32, 64, 128, 45, 90, 180, 69, 138, 57, 114, 228, 229, 231, 227, 235, 251, 219, 155, 27, 54, 108, 216, 157, 23, 46, 92, 184, 93, 186, 89, 178, 73, 146, 9, 18, 36, 72, 144, 13, 26, 52, 104, 208, 141, 55, 110, 220, 149, 7, 14, 28, 56, 112, 224, 237, 247, 195, 171, 123, 246, 193, 175, 115, 230, 225, 239, 243, 203, 187, 91, 182, 65, 130, 41, 82, 164, 101, 202, 185, 95, 190, 81, 162, 105, 210, 137, 63, 126, 252, 213, 135, 35, 70, 140, 53, 106, 212, 133, 39, 78, 156, 21, 42, 84, 168, 125, 250, 217, 159, 19, 38, 76, 152, 29, 58, 116, 232, 253, 215, 131, 43, 86, 172, 117, 234, 249, 223, 147, 11, 22, 44, 88, 176, 77, 154, 25, 50, 100, 200, 189, 87, 174, 113, 226, 233, 255, 211, 139, 59, 118, 236, 245, 199, 163, 107, 214, 129, 47, 94, 188, 85, 170, 121, 242, 201, 191, 83, 166, 97, 194, 169, 127, 254, 209, 143, 51, 102, 204, 181, 71, 142, 49, 98, 196, 165, 103, 206, 177, 79, 158, 17, 34, 68, 136, 61, 122, 244, 197, 167, 99, 198, 161, 111, 222, 145, 15, 30, 60, 120, 240, 205, 183, 67, 134, 33, 66, 132, 37, 74, 148, 5, 10, 20, 40, 80, 160, 109, 218, 153, 31, 62, 124, 248, 221, 151, 3, 6, 12, 24, 48, 96, 192, 173, 119, 238, 241, 207, 179, 75, 150, 1
]
log_table = [
    0, 0, 1, 240, 2, 225, 241, 53, 3, 38, 226, 133, 242, 43, 54, 210, 4, 195, 39, 114, 227, 106, 134, 28, 243, 140, 44, 23, 55, 118, 211, 234, 5, 219, 196, 96, 40, 222, 115, 103, 228, 78, 107, 125, 135, 8, 29, 162, 244, 186, 141, 180, 45, 99, 24, 49, 56, 13, 119, 153, 212, 199, 235, 91, 6, 76, 220, 217, 197, 11, 97, 184, 41, 36, 223, 253, 116, 138, 104, 193, 229, 86, 79, 171, 108, 165, 126, 145, 136, 34, 9, 74, 30, 32, 163, 84, 245, 173, 187, 204, 142, 81, 181, 190, 46, 88, 100, 159, 25, 231, 50, 207, 57, 147, 14, 67, 120, 128, 154, 248, 213, 167, 200, 63, 236, 110, 92, 176, 7, 161, 77, 124, 221, 102, 218, 95, 198, 90, 12, 152, 98, 48, 185, 179, 42, 209, 37, 132, 224, 52, 254, 239, 117, 233, 139, 22, 105, 27, 194, 113, 230, 206, 87, 158, 80, 189, 172, 203, 109, 175, 166, 62, 127, 247, 146, 66, 137, 192, 35, 252, 10, 183, 75, 216, 31, 83, 33, 73, 164, 144, 85, 170, 246, 65, 174, 61, 188, 202, 205, 157, 143, 169, 82, 72, 182, 215, 191, 251, 47, 178, 89, 151, 101, 94, 160, 123, 26, 112, 232, 21, 51, 238, 208, 131, 58, 69, 148, 18, 15, 16, 68, 17, 121, 149, 129, 19, 155, 59, 249, 70, 214, 250, 168, 71, 201, 156, 64, 60, 237, 130, 111, 20, 93, 122, 177, 150
]

def gf_add(a, b): return a ^ b
def gf_mul(a, b):
    if a == 0 or b == 0: return 0
    return exp_table[(log_table[a] + log_table[b]) % 255]
def gf_pow(a, n):
    if a == 0: return 0
    return exp_table[(log_table[a] * n) % 255]
def gf_inverse(n):
    if n == 0: raise ZeroDivisionError
    return exp_table[255 - log_table[n]]
def poly_eval(poly, x):
    res = 0
    for i, coeff in enumerate(poly):
        res = gf_add(res, gf_mul(coeff, gf_pow(x, i)))
    return res
def solve_linear_system(A, B):
    n = len(A)
    M = [row + [b] for row, b in zip(A, B)]
    for i in range(n):
        pivot = i
        while pivot < n and M[pivot][i] == 0:
            pivot += 1
        if pivot == n: continue
        M[i], M[pivot] = M[pivot], M[i]
        inv_val = gf_inverse(M[i][i])
        for j in range(i, n + 1): M[i][j] = gf_mul(M[i][j], inv_val)
        for k in range(n):
            if i != k:
                factor = M[k][i]
                for j in range(i, n + 1): M[k][j] = gf_add(M[k][j], gf_mul(M[i][j], factor))
    return [row[n] for row in M]

SYNDROME_COUNT = 64
KEY_LEN = 128
USER_INPUT_LEN = 64
TOTAL_LEN = USER_INPUT_LEN + KEY_LEN

FIXED_KEY = [
    0x92, 0xD5, 0x31, 0xA5, 0xE5, 0xDF, 0x29, 0x67, 0x37, 0xC8, 0x27, 0x65, 0xFE, 0x66, 0x17, 0x47,
    0x29, 0x78, 0xA5, 0x77, 0xE1, 0xAF, 0x7D, 0xD5, 0xE1, 0x5C, 0x7E, 0x66, 0xC9, 0xE9, 0x41, 0xBF,
    0xAA, 0xE0, 0x11, 0xDA, 0x39, 0x2D, 0x2D, 0x8D, 0x73, 0xB9, 0xBD, 0xC9, 0xE2, 0x86, 0x6E, 0x60,
    0x40, 0x29, 0x86, 0xBA, 0x76, 0x04, 0x8D, 0x7A, 0xC0, 0x5C, 0x89, 0x1D, 0xFF, 0x3E, 0x5E, 0x9C,
    0xE9, 0xAB, 0x45, 0x5C, 0xC1, 0x5D, 0x64, 0x56, 0x46, 0x11, 0x72, 0xCD, 0x8F, 0x5F, 0x87, 0xA9,
    0xD6, 0xB7, 0x69, 0xCF, 0x22, 0xF5, 0xF6, 0xDB, 0x41, 0x76, 0xCD, 0x3D, 0xF8, 0x66, 0x57, 0xE3,
    0x3E, 0x8F, 0x50, 0xEF, 0x1E, 0x99, 0x2A, 0x1A, 0x21, 0x58, 0xA6, 0x39, 0x38, 0x00, 0xCF, 0x81,
    0x98, 0x57, 0x61, 0x8B, 0xC7, 0x47, 0x18, 0xE3, 0x86, 0xA1, 0x5D, 0x09, 0xFB, 0xDB, 0xA1, 0x87,
]

FIXED_KEY_POLY_COEFFS = list(reversed(FIXED_KEY))

A = [[0] * USER_INPUT_LEN for _ in range(SYNDROME_COUNT)]
for j in range(SYNDROME_COUNT):
    x = gf_pow(2, j)
    for k in range(USER_INPUT_LEN):
        power = TOTAL_LEN - 1 - k
        A[j][k] = gf_pow(x, power)
B = [poly_eval(FIXED_KEY_POLY_COEFFS, gf_pow(2, j)) for j in range(SYNDROME_COUNT)]

user_input_coeffs = solve_linear_system(A, B)

final_bytes = bytes(user_input_coeffs)
b64_encoded = base64.b64encode(final_bytes)

print(b64_encoded.decode('ascii'))