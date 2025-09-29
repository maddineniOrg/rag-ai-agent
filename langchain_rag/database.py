from connection import get_db_connection


def create_application_logs():
    connection = get_db_connection()
    cursor = connection.cursor()
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

def insert_application_logs(session_id, user_query, gpt_response, model="gemini-2.0-flash-lite"):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (%s, %s, %s, %s)", (session_id, user_query, gpt_response, model))
    connection.commit()
    cursor.close()
    connection.close()

def get_chat_history(session_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT user_query, gpt_response FROM application_logs WHERE session_id = %s ORDER BY created_at", (session_id,))
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

create_application_logs()