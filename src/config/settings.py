import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
VECTORSTORES_DIR = PROJECT_ROOT /"vectorstores"

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-small",
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")