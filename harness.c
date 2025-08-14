#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;
    
    if (data[0] == 'F' && data[1] == 'U' && data[2] == 'Z' && data[3] == 'Z') {
        char *buf = malloc(size + 1);
        if (!buf) return 0;
        
        if (size > 64 * 1024) {
            free(buf);
            return 0;
        }
        
        memcpy(buf, data, size);
        buf[size] = 0;
        free(buf);
    }
    
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("usage: %s <file>\n", argv[0]);
        return 1;
    }
    
    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("fopen");
        return 1;
    }
    
    fseek(f, 0, SEEK_END);
    size_t len = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    uint8_t *buf = malloc(len);
    if (!buf) {
        printf("malloc failed\n");
        fclose(f);
        return 1;
    }
    
    fread(buf, 1, len, f);
    fclose(f);
    
    LLVMFuzzerTestOneInput(buf, len);
    free(buf);
    return 0;
}
