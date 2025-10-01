import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from telegram_bot.controller import telegram_bot_router

client = TestClient(telegram_bot_router)

# Minimal valid user
user = {
    "id": 123,
    "is_bot": True,
    "first_name": "Bot",
    "username": "botuser"
}
user_human = {
    "id": 456,
    "is_bot": False,
    "first_name": "Alice",
    "username": "alice"
}

# Minimal valid chat
chat = {
    "id": 789,
    "type": "private"
}

# Minimal valid message
message = {
    "message_id": 1,
    "from": user_human,
    "chat": chat,
    "text": "hello"
}

# Minimal valid my_chat_member
my_chat_member_bot = {
    "chat": chat,
    "date": 111111,
    "from": user_human,
    "old_chat_member": {"status": "member", "user": user},
    "new_chat_member": {"status": "member", "user": user}
}
my_chat_member_kicked = {
    "chat": chat,
    "date": 111111,
    "from": user_human,
    "old_chat_member": {"status": "member", "user": user_human},
    "new_chat_member": {"status": "kicked", "user": user_human}
}
my_chat_member_member = {
    "chat": chat,
    "date": 111111,
    "from": user_human,
    "old_chat_member": {"status": "kicked", "user": user_human},
    "new_chat_member": {"status": "member", "user": user_human}
}

@patch("telegram_bot.controller.process_message")
def test_handle_message_is_bot(mock_process):
    payload = {
        "update_id": 1000,
        "my_chat_member": my_chat_member_bot,
        "message": message
    }
    response = client.post("/telegram/message", json=payload)
    assert response.text == "Message Ignored"
    mock_process.assert_not_called()

@patch("telegram_bot.controller.process_message")
def test_handle_message_kicked(mock_process):
    payload = {
        "update_id": 1001,
        "my_chat_member": my_chat_member_kicked,
        "message": message
    }
    response = client.post("/telegram/message", json=payload)
    assert response.text == "Message Ignored"
    mock_process.assert_not_called()

@patch("telegram_bot.controller.process_message")
def test_handle_message_normal(mock_process):
    payload = {
        "update_id": 1002,
        "my_chat_member": my_chat_member_member,
        "message": message
    }
    response = client.post("/telegram/message", json=payload)
    assert response.text == "Message Processed"
    mock_process.assert_called_once()

@patch("telegram_bot.controller.process_message")
def test_handle_message_no_my_chat_member(mock_process):
    payload = {
        "update_id": 1003,
        "message": message
    }
    response = client.post("/telegram/message", json=payload)
    assert response.text == "Message Processed"
    mock_process.assert_called_once()

@patch("telegram_bot.controller.process_message", side_effect=Exception("fail"))
def test_handle_message_exception(mock_process):
    payload = {
        "update_id": 1004,
        "message": message
    }
    response = client.post("/telegram/message", json=payload)
    assert response.text == "Message Processed"
    mock_process.assert_called_once()
