# EPSODAY

Zero-day research framework.

## Quick Start
```bash
make && python3 main.py -t ./harness -f
```
## Components
- fuzz.py - AFL++ integration
- triage.py - crash analysis
- evasion.py - EDR bypass
- delivery.py - C2 payload delivery
- rust_exploit/ - memory-safe exploits

## Test
```bash
python3 -m pytest tests/
```

## Docker
```bash
docker build -t epsoday .
docker run -v $(pwd)/targets:/app/targets epsoday
```

**LICENSE** (MIT):
    Copyright 2025, CHOKRI Faysal

**setup.sh**:
```bash
#!/bin/bash
sudo apt update && sudo apt install -y afl++ gcc python3 cargo
python3 -m pip install -r requirements.txt
cargo build --release
make
echo "EPSODAY ready"
```

