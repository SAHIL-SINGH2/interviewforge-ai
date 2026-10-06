@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
