import os

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import create_history_aware_retriever


class Document:

    # Loading all the documents in given path
    def load(self, folder_path):
        """
        Loads all documents from the given folder path
        """

        documents = []
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if (file_name.endswith(".pdf")):
                loader = PyPDFLoader(file_path)
            elif (file_name.endswith(".docx")):
                loader = Docx2txtLoader(file_path)
            else:
                print(f"Unsupported file type: {file_name}")
                continue
            documents.extend(loader.load())
        return documents

    # Splitting the documents
    def split(self, documents, chunk_size=1000, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        splits = text_splitter.split_documents(documents)
        return splits

    # Embedding the Documents
    def embed(self, documents, embedding_model="models/gemini-embedding-001", model_provider="google_genai"):
        if (model_provider == "google_genai"):
            embeddings = GoogleGenerativeAIEmbeddings(model_name=embedding_model)
        embedded_documents = embeddings.embed_documents([document.page_content for document in documents])
        return embedded_documents

    def get_embedding_function(self, embedding_model, model_provider):
        if (model_provider == "google_genai"):
            embedding_function = GoogleGenerativeAIEmbeddings(model=embedding_model)
            return embedding_function
        elif (model_provider == "openai"):
            embedding_function = OpenAIEmbeddings(model=embedding_model)
            return embedding_function
        elif (model_provider == "huggingface"):
            embedding_function = HuggingFaceEmbeddings(model_name=embedding_model)
            return embedding_function
        else:
            print(f"Invalid model provider: {model_provider}")
            return None

    # Store the Documents
    def store(self, documents, embedding_model="models/gemini-embedding-001", model_provider="google_genai",
                        vector_store="chroma", collection_name="my_collection"):
        embedding_function = self.get_embedding_function(embedding_model, model_provider)
        assert embedding_function is not None, "Embedding function not found"

        if (vector_store == "chroma"):
            vector_store = Chroma.from_documents(collection_name=collection_name, documents=documents,
                                                 embedding=embedding_function)
            print("Vector Store created and persisted to './content/chroma_langchain_db'")
        else:
            print(f"Invalid vector store: {vector_store}")
            return None
        return vector_store

class Retriever:

    # Retrieves the related documents
    def create(self, vector_store, matching_documents=10):
        retriever = vector_store.as_retriever(search_args={"k": matching_documents})
        # retriever.invoke(query)
        return retriever

    def history_aware_retriever(self, llm, retriever, contextualize_question_prompt):
        retriever = create_history_aware_retriever(
            llm, retriever, contextualize_question_prompt
        )

        # retriever.invoke({"input": question2, "chat_history": chat_history})
        return retriever