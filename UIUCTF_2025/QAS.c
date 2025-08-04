#include <stdio.h>
#include <stdint.h>

typedef short int_small;
typedef int not_int_big;
typedef unsigned char quantum_byte;

static inline quantum_byte generate_quantum_entropy() {
    static quantum_byte seed = 0x42;
    seed = ((seed << 3) ^ (seed >> 5)) + 0x7f;
    return seed;
}

not_int_big calculate_intermediate_hash(int_small input_val, quantum_byte* entropy) {
    not_int_big hash = input_val;

    hash ^= (entropy[0] << 8) | entropy[1];
    hash ^= (entropy[2] << 4) | (entropy[3] >> 4);
    hash += (entropy[4] * entropy[5]) & 0xff;
    hash ^= entropy[6] ^ entropy[7];
    hash |= 0xeee;

    return hash;
}


int main() {
    quantum_byte entropy_pool[8];
    for (int i = 0; i < 8; i++) {
        entropy_pool[i] = generate_quantum_entropy();
    }
    int_small input_val_part = 0;
    not_int_big target_hash = 0x555;

    not_int_big intermediate_hash = calculate_intermediate_hash(input_val_part, entropy_pool);
    printf("Intermediate hash (when input.val is 0): 0x%x\n", intermediate_hash);


    not_int_big required_padding_part = intermediate_hash ^ target_hash;
    printf("Required padding value to get 0x555: 0x%x\n", required_padding_part);
    required_padding_part = ((required_padding_part & 0x00FF)<<8) | ((required_padding_part & 0xFF00) >> 8);
    uint32_t final_input = (required_padding_part << 16) | (uint16_t)input_val_part;

    printf("\nThe correct input value is: %u (or %d as signed)\n", final_input, (int)final_input);

    return 0;
}