#!/bin/bash

echo "EPSODAY Test Suite"
echo "=================="

# Build everything
echo "Building..."
make clean && make

# Run unit tests
echo "Running unit tests..."
python3 -m pytest tests/ -v

# Run integration tests
echo "Running integration tests..."
python3 tests/integration/test_full_pipeline.py

# Run fuzz tests
echo "Running fuzz regression..."
python3 test_runner.py

echo "All tests complete"
