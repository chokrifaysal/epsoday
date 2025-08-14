#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 4) return 0;  // whatever
    
    // basic parsing 
    if (data[0] == 'F' && data[1] == 'U' && data[2] == 'Z' && data[3] == 'Z') {
        char buf[32];
        // this is the vuln 
        if (size > 32) {
            memcpy(buf, data, size);  // boom
        }
    }
    
    // TODO: add more checks here
    return 0;
}

// main for testing - remove this later
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
        return 1;
    }
    
    fread(buf, 1, len, f);
    fclose(f);
    
    LLVMFuzzerTestOneInput(buf, len);
    free(buf);
    
    printf("done\n");
    return 0;
}
