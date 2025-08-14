#!/bin/bash
set -e

echo "Running tests..."

make clean && make
python3 -m pytest tests/ -v --tb=short
cargo test --manifest-path rust_exploit/Cargo.toml

echo "All tests passed"
