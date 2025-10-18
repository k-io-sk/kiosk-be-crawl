import mysql.connector
from dotenv import load_dotenv
from pathlib import Path
import os

# ------------------------------
# 전역 변수 설정
# ------------------------------
env = os.environ.get("ENV", "local")
BASE_DIR = Path(__file__).resolve().parent

if env == "local":
    load_dotenv(BASE_DIR / ".env.local")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# ------------------------------
# mysql connector 반환 함수
# ------------------------------
def get_conn():
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

    return conn