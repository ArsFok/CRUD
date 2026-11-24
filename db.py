
import os

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


# Загружаем настройки из .env
load_dotenv()


# Функция подключения к PostgreSQL
def get_connection():

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        row_factory=dict_row
    )
