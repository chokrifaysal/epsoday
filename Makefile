CC = gcc
CFLAGS = -O3 -g -fsanitize=address
TARGET = harness

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    CFLAGS += -D_GNU_SOURCE
endif
ifeq ($(UNAME_S),Darwin)
    CFLAGS += -D_DARWIN_C_SOURCE
endif

all: $(TARGET)

$(TARGET): harness.c
	$(CC) $(CFLAGS) -o $(TARGET) harness.c

clean:
	rm -f $(TARGET) *.o

test: $(TARGET)
	python3 -m pytest tests/ -v

.PHONY: all clean test
