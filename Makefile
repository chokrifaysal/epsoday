CC = gcc
# CC = afl-clang-fast  # breaks on my system
CFLAGS = -O3 -g -fsanitize=address
# CFLAGS = -O0 -g  # use this for debugging
TARGET = harness

all: $(TARGET)

$(TARGET): harness.c
	$(CC) $(CFLAGS) -o $(TARGET) harness.c
	# strip $(TARGET)  # uncomment for smaller binary

clean:
	rm -f $(TARGET) *.o
	# rm -rf findings/  # careful with this

# TODO: add test target
# test: $(TARGET)
# 	A
# 	./$(TARGET) test_input
