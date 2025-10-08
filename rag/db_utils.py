from connection import get_db_connection

# Creating Database Tables
def create_application_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_logs(
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_query TEXT NOT NULL,
                gpt_response TEXT NOT NULL,
                model VARCHAR(100) DEFAULT 'gpt-3.5-turbo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
    conn.commit()
    cursor.close()
    conn.close()

def create_document_store():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_store(
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


# Managing Chat Logs
def insert_application_logs(session_id, user_query, gpt_response, model="gemini-2.0-flash-lite"):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (%s, %s, %s, %s)",
        (session_id, user_query, gpt_response, model))
    connection.commit()
    cursor.close()
    connection.close()

def get_chat_history(session_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_query, gpt_response FROM application_logs WHERE session_id = %s ORDER BY created_at",
        (session_id,))
    rows = cursor.fetchall()
    messages = []
    for row in rows:
        messages.extend([
            {"role": "human", "content": row[0]},
            {"role": "ai", "content": row[1]}
        ])
    cursor.close()
    connection.close()
    return messages


# Managing Document Records
def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO document_store (filename) VALUES (%s)", (filename,))
    conn.commit()
    file_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return file_id

def delete_document_record(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM document_store WHERE id = %s", (file_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC")
    rows = cursor.fetchall()
    documents = [{"id": row[0], "filename": row[1], "upload_timestamp": row[2]} for row in rows]
    cursor.close()
    conn.close()
    return documents

# Initialize the database tables
create_application_logs()
create_document_store()

