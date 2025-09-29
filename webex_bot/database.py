import uuid

from torchgen.api.cpp import return_type

from connection import get_db_connection


def create_room_details():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_details(
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_id VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
                   )
    connection.commit()
    cursor.close()
    connection.close()

def insert_room_details(room_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    session_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO room_details (room_id, session_id) VALUES (%s, %s)", (room_id, session_id))
    connection.commit()
    cursor.close()
    connection.close()
    return session_id

def get_session_id(room_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT session_id FROM room_details WHERE room_id = %s", (room_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if row:
        return row[0]
    return insert_room_details(room_id)

create_room_details()