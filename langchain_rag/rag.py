import os
import uuid

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_history_aware_retriever

from langchain_rag.database import create_application_logs, get_chat_history, insert_application_logs


# Setting Langsmith Environment
def set_langsmith_environment():
    """

    :return:
    """
    load_dotenv()
    os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
    os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

# Setting Google API key
def set_google_environment():
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Building LLM (Google Gemini)
def build_llm(model="gemini-2.0-flash-lite", model_provider="google_genai"):
    if(model_provider == "google_genai"):
        llm = init_chat_model(model, model_provider=model_provider)
        return llm
    elif(model_provider == "huggingface"):
        #from langchain_community.llms import HuggingFaceHub
        from langchain_community.llms import HuggingFacePipeline
        from transformers import pipeline

        generator = pipeline("text2text-generation", model=model)
        llm = HuggingFacePipeline(pipeline=generator)
        #llm = HuggingFaceHub(repo_id=model, model_kwargs={"temperature": 0.7, "max_new_tokens": 256})
        return llm

# Building Output Parser
def build_output_parser():
    parser = StrOutputParser()
    return parser

# Loading all the documents in given path
def load_documents(folder_path):
    """
    Loads all documents from the given folder path
    """

    documents = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if(file_name.endswith(".pdf")):
            loader = PyPDFLoader(file_path)
        elif(file_name.endswith(".docx")):
            loader = Docx2txtLoader(file_path)
        else:
            print(f"Unsupported file type: {file_name}")
            continue
        documents.extend(loader.load())
    return documents

# Splitting the documents
def split_documents(documents, chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = text_splitter.split_documents(documents)
    return splits

# Embedding the Documents
def embed_documents(documents, embedding_model="models/gemini-embedding-001", model_provider="google_genai"):
    if(model_provider == "google_genai"):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(model_name=embedding_model)
    embedded_documents = embeddings.embed_documents([document.page_content for document in documents])
    return embedded_documents

def get_embedding_function(embedding_model, model_provider):
    if(model_provider == "google_genai"):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embedding_function = GoogleGenerativeAIEmbeddings(model=embedding_model)
        return embedding_function
    elif(model_provider == "openai"):
        from langchain_openai import OpenAIEmbeddings
        embedding_function = OpenAIEmbeddings(model=embedding_model)
        return embedding_function
        pass
    elif(model_provider == "huggingface"):
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embedding_function = HuggingFaceEmbeddings(model_name=embedding_model)
        return embedding_function
    else:
        print(f"Invalid model provider: {model_provider}")
        return None


# Store the Documents
def store_documents(documents, embedding_model="models/gemini-embedding-001", model_provider="google_genai",
                    vector_store="chroma", collection_name="my_collection"):
    embedding_function = get_embedding_function(embedding_model, model_provider)
    assert embedding_function is not None, "Embedding function not found"

    if (vector_store == "chroma"):
        from langchain.vectorstores import Chroma
        vector_store = Chroma.from_documents(collection_name=collection_name, documents=documents,
                                             embedding=embedding_function)
        print("Vector Store created and persisted to './content/chroma_langchain_db'")
    else:
        print(f"Invalid vector store: {vector_store}")
        return None
    return vector_store

# Retrieves the related documents
def create_retriever(vector_store, matching_documents=10):
    retriever = vector_store.as_retriever(search_args={"k": matching_documents})
    #retriever.invoke(query)
    return retriever

# Creates chat prompt
def create_chat_prompt():
    template = """
    Answer the question based on the following context:
    {context}
    
    If anybody ask about you, say them that Anil has created you for his personal use.

    Question: {question}

    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt

def doc2str(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def build_rag_chain(retriever, prompt, llm):
    rag_chain = (
        {"context": retriever | doc2str, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def build_contenxualize_question_prompt():

    contenxualize_qa_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contenxualize_question_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contenxualize_qa_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ]
    )
    return contenxualize_question_prompt


def history_aware_retriever(llm, retriever, contenxualize_question_prompt):
    retriever = create_history_aware_retriever(
        llm, retriever, contenxualize_question_prompt
    )

    #history_aware_retriever.invoke({"input": question2, "chat_history": chat_history})
    return retriever


def build_conversational_rag_chain(llm):
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can answer questions about RGUKT.Use the following context to answer the use's question"),
        ("system", "Context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    return question_answer_chain


def ask_rag(question, session_id=None):
    set_langsmith_environment()
    set_google_environment()
    documents = load_documents("/Users/anil/Downloads/rag_documents")
    splits = split_documents(documents)
    # vector_store = store_documents(splits, embedding_model="text-embedding-3-small", model_provider="openai")
    vector_store = store_documents(splits, embedding_model="sentence-transformers/all-MiniLM-L6-v2", model_provider="huggingface")
    # llm = build_llm(model="google/flan-t5-base", model_provider="huggingface")
    llm = build_llm()

    retriever = create_retriever(vector_store, 2)
    prompt = create_chat_prompt()
    # rag_chain = build_rag_chain(retriever, prompt, llm)

    contenxualize_question_prompt = build_contenxualize_question_prompt()
    ha_retriever = history_aware_retriever(llm, retriever, contenxualize_question_prompt)
    question_answer_chain = build_conversational_rag_chain(llm)
    conversational_rag_chain = create_retrieval_chain(ha_retriever, question_answer_chain)


    chat_history = get_chat_history(session_id)
    response = conversational_rag_chain.invoke({"input": question, "chat_history": chat_history})
    insert_application_logs(session_id,  question, response["answer"])
    chat_history.extend([HumanMessage(content=question), AIMessage(content=response["answer"])])
    return response["answer"]

