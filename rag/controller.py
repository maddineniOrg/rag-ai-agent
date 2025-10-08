from fastapi import File, UploadFile, HTTPException, APIRouter
from rag.pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from rag.langchain_utils import get_rag_chain
from rag.db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
from rag.chroma_utils import index_document_to_chroma, delete_doc_from_chroma

import os
import uuid
import logging
import shutil

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Initialize FastAPI app
router = APIRouter()

# Chat Endpoint
@router.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

    chat_history = get_chat_history(session_id)
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })['answer']

    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    response = QueryResponse(answer=answer, session_id=session_id, model=query_input.model)
    return response

# Upload Document Endpoint
@router.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".docx", ".html"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")

    temp_file_path = f"/tmp/{uuid.uuid4()}{file_extension}"

    try:
        # save the uploaded file to a temporary location
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)
        if success:
            return {"message": f"File {file.filename} uploaded and indexed successfully.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        file.file.close()

# List Documents Endpoint
@router.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    documents = get_all_documents()
    return [DocumentInfo(id=doc['id'], filename=doc['filename'], upload_timestamp=doc['upload_timestamp']) for doc in documents]

# Delete Document Endpoint
@router.delete("/delete-doc")
def delete_document(request: DeleteFileRequest):
    chroma_delete_success = delete_doc_from_chroma(request.file_id)
    if chroma_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {"message": f"File with ID {request.file_id} deleted successfully from the system."}
        else:
            return {"error", f"Deleted from Chroma but failed to delete DB record for file ID {request.file_id}."}
    else:
        return {"error", f"Failed to delete file with ID {request.file_id} from Chroma."}


