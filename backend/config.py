from pathlib import Path
import os

BASE_DIR=Path(__file__).resolve().parents[1]
DATA_DIR=BASE_DIR/'data'
DB_PATH=DATA_DIR/'interview_accelerator.db'
APP_NAME='InterviewForge AI'
AI_PROVIDER=os.getenv('AI_PROVIDER','local').lower()
GROQ_API_KEY=os.getenv('GROQ_API_KEY','')
GROQ_MODEL=os.getenv('GROQ_MODEL','llama-3.3-70b-versatile')
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY','')
OPENAI_BASE_URL=os.getenv('OPENAI_BASE_URL','https://api.openai.com/v1')
OPENAI_MODEL=os.getenv('OPENAI_MODEL','gpt-4o-mini')
