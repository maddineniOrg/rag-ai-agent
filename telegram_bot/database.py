import uuid

from connection import get_db_connection


def create_chat_details():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_details(
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
                   )
    connection.commit()
    cursor.close()
    connection.close()

def insert_chat_details(chat_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    session_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO chat_details (chat_id, session_id) VALUES (%s, %s)", (chat_id, session_id))
    connection.commit()
    cursor.close()
    connection.close()
    return session_id

def get_session_id(chat_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT session_id FROM chat_details WHERE chat_id = %s", (chat_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if row:
        return row[0]
    return insert_chat_details(chat_id)

create_chat_details()