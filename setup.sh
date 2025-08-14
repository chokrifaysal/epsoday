#!/bin/bash
set -e

echo "Installing EPSODAY..."

if command -v apt-get &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y build-essential afl++ python3-pip gdb
elif command -v brew &> /dev/null; then
    brew install afl-fuzz python3
elif [[ "$OSTYPE" == "msys" ]]; then
    echo "Windows detected - install WSL or use install.py"
    exit 1
fi

pip3 install -r requirements.txt
cargo build --release --manifest-path rust_exploit/Cargo.toml
make

echo "EPSODAY installed"
