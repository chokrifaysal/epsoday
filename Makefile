CC = gcc
CFLAGS = -O3 -g -fsanitize=address

ifeq ($(OS),Windows_NT)
    TARGET = harness.exe
    RM = del
else
    TARGET = harness
    RM = rm -f
endif

all: $(TARGET)

$(TARGET): harness.c
	$(CC) $(CFLAGS) -o $(TARGET) harness.c

clean:
	$(RM) $(TARGET) *.o

test:
	python3 -m pytest tests/ -v

install:
	python3 install.py

.PHONY: all clean test install
