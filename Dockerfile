FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    gdb \
    afl++ \
    sqlite3 \
    curl \
    git \
    rustc \
    cargo \
    valgrind

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN cd rust_exploit && cargo build --release && cd ..
RUN make

EXPOSE 8080

CMD ["python3", "main.py", "--help"]
