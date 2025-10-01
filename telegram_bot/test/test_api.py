import os
import pytest
from unittest.mock import patch, MagicMock
import telegram_bot.api as api

@patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "dummy_token"})
@patch("httpx.Client")
def test_send_message_success(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200  # Ensure status_code is set for success
    mock_response.text = "OK"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    api.send_message("12345", "Hello")
    mock_client.post.assert_called_once()
    captured = capsys.readouterr()
    assert "Message sent successfully" in captured.out

@patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "dummy_token"})
@patch("httpx.Client")
def test_send_message_failure(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    api.send_message("12345", "Hello")
    captured = capsys.readouterr()
    assert "Failed to send message: Bad Request" in captured.out

@patch.dict(os.environ, {}, clear=True)
@patch("httpx.Client")
def test_send_message_no_token(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    api.send_message("12345", "Hello")
    mock_client.post.assert_called_once()
    captured = capsys.readouterr()
    assert "Message sent successfully" in captured.out
