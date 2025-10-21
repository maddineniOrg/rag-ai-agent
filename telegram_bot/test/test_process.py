import sys
import types
import pytest
from unittest.mock import patch, MagicMock

# Patch database imports before importing process
sys.modules["telegram_bot.database"] = types.SimpleNamespace(get_session_id=lambda x: None, insert_chat_details=lambda x, y: None)

from telegram_bot.process import delete_file_from_rag, upload_file_to_rag, ask_rag, handle_question, handle_document_upload, process_message
from telegram_bot.models import Document, RagResponse, Chat, FromUser, Message
from langchain_google_genai._common import GoogleGenerativeAIError

def make_message(text=None):
    chat = Chat(first_name="A", id=1, type="private")
    from_ = FromUser(first_name="A", id=2, is_bot=False)
    return Message(chat=chat, from_=from_, message_id=1, text=text)

@patch("httpx.Client")
def test_delete_file_from_rag_success(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_client.request.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    result = delete_file_from_rag(123)
    assert result is True

@patch("httpx.Client")
def test_delete_file_from_rag_failure(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Not Found"
    mock_client.request.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    result = delete_file_from_rag(123)
    assert result is False
    captured = capsys.readouterr()
    assert "Failed to delete file from RAG service: Not Found" in captured.out

@patch("httpx.Client")
def test_delete_file_from_rag_exception(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_client.request.side_effect = Exception("Network error")
    mock_client_class.return_value.__enter__.return_value = mock_client

    # Should print the exception and return False
    result = delete_file_from_rag(123)
    assert result is False
    captured = capsys.readouterr()
    assert "Failed to delete file from RAG service" in captured.out or "Network error" in captured.out

@patch("httpx.Client")
def test_upload_file_to_rag_success(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file_id": "abc123"}
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    doc = Document(file_id="1", file_unique_id="u1", file_name="test.txt", mime_type="text/plain", file_content=b"hello")
    file_id = upload_file_to_rag(doc)
    assert file_id == "abc123"

@patch("httpx.Client")
def test_upload_file_to_rag_failure(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Upload failed"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    doc = Document(file_id="1", file_unique_id="u1", file_name="test.txt", mime_type="text/plain", file_content=b"hello")
    with pytest.raises(TypeError) as excinfo:
        upload_file_to_rag(doc)
    assert "Failed to upload file to RAG service: Upload failed" in str(excinfo.value)

@patch("httpx.Client")
def test_upload_file_to_rag_exception(mock_client_class):
    mock_client = MagicMock()
    mock_client.post.side_effect = Exception("Network error")
    mock_client_class.return_value.__enter__.return_value = mock_client

    doc = Document(file_id="1", file_unique_id="u1", file_name="test.txt", mime_type="text/plain", file_content=b"hello")
    with pytest.raises(Exception) as excinfo:
        upload_file_to_rag(doc)
    assert "Network error" in str(excinfo.value)

@patch("httpx.Client")
def test_ask_rag_success(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"session_id": "sess1", "answer": "42", "model": "gemini-2.0-flash-lite"}
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    result = ask_rag("What is the answer?", "sess1")
    assert isinstance(result, RagResponse)
    assert result.session_id == "sess1"
    assert result.answer == "42"
    assert result.model == "gemini-2.0-flash-lite"

@patch("httpx.Client")
def test_ask_rag_failure(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    result = ask_rag("What is the answer?", "sess1")
    assert result is None
    captured = capsys.readouterr()
    assert "Failed to get response from RAG service: Bad request" in captured.out

@patch("httpx.Client")
def test_ask_rag_exception(mock_client_class):
    mock_client = MagicMock()
    mock_client.post.side_effect = Exception("Network error")
    mock_client_class.return_value.__enter__.return_value = mock_client

    with pytest.raises(Exception):
        ask_rag("What is the answer?", "sess1")

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.delete_file_from_rag")
def test_handle_question_delete(mock_delete, mock_send):
    mock_delete.return_value = True
    handle_question("/delete 42", 1, 2)
    mock_delete.assert_called_once_with(42)
    mock_send.assert_called_once_with(1, "File deleted successfully with file_id: 42", 2)

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.insert_chat_details")
@patch("telegram_bot.process.ask_rag")
@patch("telegram_bot.process.get_session_id")
def test_handle_question_success(mock_get_session_id, mock_ask_rag, mock_insert, mock_send):
    mock_get_session_id.return_value = "sess1"
    mock_ask_rag.return_value = RagResponse(answer="answer", session_id="sess1", model="m")
    handle_question("What?", 1, 2)
    mock_insert.assert_called_once_with(1, "sess1")
    mock_send.assert_called_once_with(1, "answer", 2)

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.ask_rag")
@patch("telegram_bot.process.get_session_id")
def test_handle_question_internal_error(mock_get_session_id, mock_ask_rag, mock_send):
    mock_get_session_id.return_value = "sess1"
    mock_ask_rag.return_value = None
    handle_question("What?", 1, 2)
    mock_send.assert_called_once_with(1, "Unable to Process your Question, Due to Internal Error", 2)

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.get_session_id")
def test_handle_question_google_genai_error(mock_get_session_id, mock_send, capsys):
    mock_get_session_id.side_effect = GoogleGenerativeAIError("fail")
    handle_question("What?", 1, 2)
    mock_send.assert_called_once_with(1, "fail", 2)
    captured = capsys.readouterr()
    assert "fail" in captured.out

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.upload_file_to_rag")
@patch("telegram_bot.process.download_telegram_file")
def test_handle_document_upload_success(mock_download, mock_upload, mock_send):
    mock_download.return_value = b"filecontent"
    mock_upload.return_value = "fileid123"
    doc = Document(file_id="f1", file_unique_id="u1", file_name="test.txt", mime_type="text/plain")
    handle_document_upload(doc, 1, 2)
    assert doc.file_content == b"filecontent"
    mock_upload.assert_called_once_with(doc)
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 1 and args[2] == 2
    assert "File uploaded successfully" in args[1]
    assert "fileid123" in args[1]

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.upload_file_to_rag")
@patch("telegram_bot.process.download_telegram_file")
def test_handle_document_upload_failure(mock_download, mock_upload, mock_send):
    mock_download.return_value = b"filecontent"
    mock_upload.return_value = None
    doc = Document(file_id="f1", file_unique_id="u1", file_name="test.txt", mime_type="text/plain")
    handle_document_upload(doc, 1, 2)
    mock_upload.assert_called_once_with(doc)
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 1 and args[2] == 2
    assert "Failed to upload the file" in args[1]

@patch("telegram_bot.process.send_message")
@patch("telegram_bot.process.upload_file_to_rag")
@patch("telegram_bot.process.download_telegram_file")
def test_handle_document_upload_typeerror(mock_download, mock_upload, mock_send):
    mock_download.return_value = b"filecontent"
    mock_upload.side_effect = TypeError("fail upload")
    doc = Document(file_id="f1", file_unique_id="u1", file_name="test.txt", mime_type="text/plain")
    handle_document_upload(doc, 1, 2)
    mock_upload.assert_called_once_with(doc)
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == 1 and args[2] == 2
    assert "fail upload" in args[1]

@patch("telegram_bot.process.handle_document_upload")
@patch("telegram_bot.process.handle_question")
def test_process_message_document(mock_handle_question, mock_handle_document_upload):
    # Document present, should call handle_document_upload
    msg = MagicMock()
    msg.text = None
    msg.document = "doc_obj"
    msg.chat.id = 1
    msg.message_id = 2
    process_message(msg)
    mock_handle_document_upload.assert_called_once_with("doc_obj", 1, 2)
    mock_handle_question.assert_not_called()

@patch("telegram_bot.process.handle_document_upload")
@patch("telegram_bot.process.handle_question")
def test_process_message_question(mock_handle_question, mock_handle_document_upload):
    # No document, but question present, should call handle_question
    msg = MagicMock()
    msg.text = "What is this?"
    msg.document = None
    msg.chat.id = 1
    msg.message_id = 2
    process_message(msg)
    mock_handle_question.assert_called_once_with("What is this?", 1, 2)
    mock_handle_document_upload.assert_not_called()

@patch("telegram_bot.process.handle_document_upload")
@patch("telegram_bot.process.handle_question")
def test_process_message_none(mock_handle_question, mock_handle_document_upload):
    # Neither document nor question, should call neither
    msg = MagicMock()
    msg.text = None
    msg.document = None
    msg.chat.id = 1
    msg.message_id = 2
    result = process_message(msg)
    mock_handle_document_upload.assert_not_called()
    mock_handle_question.assert_not_called()
    assert result is None
