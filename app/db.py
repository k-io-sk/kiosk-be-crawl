import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os

env = os.environ.get("ENV", "local")
BASE_DIR = Path(__file__).resolve().parent

if env == "local":
    load_dotenv(BASE_DIR / ".env.local")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

def get_conn():
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

    return conn