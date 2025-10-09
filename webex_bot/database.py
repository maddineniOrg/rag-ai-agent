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

def create_message_details():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_details(
            child_message_id VARCHAR(255) PRIMARY KEY,
            parent_message_id VARCHAR(255) NOT NULL
        )
    """
                   )
    connection.commit()
    cursor.close()
    connection.close()

def create_file_details():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_details(
            rag_file_id INT PRIMARY KEY,
            webex_file_id VARCHAR(255) NOT NULL,
            webex_message_id VARCHAR(255) NOT NULL
        )
    """
                   )
    connection.commit()
    cursor.close()
    connection.close()
    print("Returning from create_file_details")

def insert_room_details(room_id, session_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO room_details (room_id, session_id) VALUES (%s, %s)", (room_id, session_id))
    connection.commit()
    cursor.close()
    connection.close()
    return None

def get_session_id(room_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT session_id FROM room_details WHERE room_id = %s", (room_id,))
    row = cursor.fetchone()
    cursor.close()
    connection.close()
    if row:
        return row[0]
    return None

def insert_message_details(child_message_id, parent_message_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO message_details (child_message_id, parent_message_id) VALUES (%s, %s)", (child_message_id, parent_message_id))
    connection.commit()
    cursor.close()
    connection.close()
    return None

def delete_message_details(parent_message_id: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM message_details WHERE parent_message_id = %s", (parent_message_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return None

def get_child_message_ids(parent_message_id: str) -> list[str]:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT child_message_id FROM message_details WHERE parent_message_id = %s", (parent_message_id,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [row[0] for row in rows]

def insert_file_details(rag_file_id, webex_file_id, webex_message_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO file_details (rag_file_id, webex_file_id, webex_message_id) VALUES (%s, %s, %s)", (rag_file_id, webex_file_id, webex_message_id))
    connection.commit()
    cursor.close()
    connection.close()
    return None

def get_rag_file_ids(webex_message_id: str) -> list[int]:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT rag_file_id FROM file_details WHERE webex_message_id = %s", (webex_message_id,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return [row[0] for row in rows]


create_room_details()
create_message_details()
create_file_details()