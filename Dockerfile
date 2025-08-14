
RUN apt-get update && apt-get install -y \
    gcc \
    python3 \
    python3-pip \
    gdb \
    afl++ \
    sqlite3 \
    curl \
    git \
    rustc \
    cargo

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
RUN make

EXPOSE 8080

CMD ["python3", "main.py", "--help"]
