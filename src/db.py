import os
import psycopg
from dotenv import load_dotenv

load_dotenv()  # reads the .env file


def get_connection():
    return psycopg.connect(os.environ["DATABASE_URL"])