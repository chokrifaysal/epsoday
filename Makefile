CC = gcc
CFLAGS = -O3 -g -fsanitize=address
TARGET = harness

all: $(TARGET)

$(TARGET): harness.c
	$(CC) $(CFLAGS) -o $(TARGET) harness.c

clean:
	rm -f $(TARGET) *.o
