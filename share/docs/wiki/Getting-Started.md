# Getting Started

Follow the SOP in `instruction.md` for detailed setup. Below is the quick summary.

## Server (dev)
```bash
cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python run.py
```

## Edge (device)
```bash
cd edge
bash setup_env.sh
gunicorn --config gunicorn_config.py v1_3.src.wsgi:app
```

## Sparse checkout (machines only needing server or edge)
```bash
# Server machine
git clone --filter=blob:none --sparse <repo> /opt/monorepo
cd /opt/monorepo && git switch monorepo/initial && git sparse-checkout set server share

# Edge machine
git clone --filter=blob:none --sparse <repo> /opt/monorepo
cd /opt/monorepo && git switch monorepo/initial && git sparse-checkout set edge share
```