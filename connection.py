from dotenv import load_dotenv
import os
import pymysql as sql

load_dotenv()
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
port = int(os.getenv("DB_PORT"))

def get_db_connection():
    connection = sql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    return connection