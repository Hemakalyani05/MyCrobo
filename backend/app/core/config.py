import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SAMPLE_REPOS_DIR = WORKSPACE_DIR / "sample_repos"

DATABASE_PATH = DATA_DIR / "codesentinel.db"

PROJECT_NAME = "CodeSentinel AI"
VERSION = "1.0.0"
DESCRIPTION = "Architecture-Agnostic AI Code Security & Quality Review Agent"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "heuristic")  # heuristic, gemini, openai, ollama
