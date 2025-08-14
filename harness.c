#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;
    
    // basic parsing to trigger bugs
    if (data[0] == 'F' && data[1] == 'U' && data[2] == 'Z' && data[3] == 'Z') {
        char buf[32];
        if (size > 32) {
            memcpy(buf, data, size);  // potential overflow
        }
    }
    
    return 0;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;
    
    fseek(f, 0, SEEK_END);
    size_t len = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    uint8_t *buf = malloc(len);
    fread(buf, 1, len, f);
    fclose(f);
    
    LLVMFuzzerTestOneInput(buf, len);
    free(buf);
    return 0;
}
