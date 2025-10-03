
from langchain.chat_models import init_chat_model
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_history_aware_retriever
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

from langchain_rag.database import RagDB
from langchain_rag.setup import Setup
from langchain_rag.vectorstore import Document, Retriever


class LLM:

    def __init__(self):
        self.setup = Setup()
        self.document = Document()
        self.retriever = Retriever()
        self.prompt = Prompt()

        self.db = RagDB()

    # Building LLM (Google Gemini)
    def build_llm(self, model="gemini-2.0-flash-lite", model_provider="google_genai"):
        if (model_provider == "google_genai"):
            llm = init_chat_model(model, model_provider=model_provider)
            return llm
        elif (model_provider == "huggingface"):
            # from langchain_community.llms import HuggingFaceHub

            generator = pipeline("text2text-generation", model=model)
            llm = HuggingFacePipeline(pipeline=generator)
            # llm = HuggingFaceHub(repo_id=model, model_kwargs={"temperature": 0.7, "max_new_tokens": 256})
            return llm

    # Building Output Parser
    def build_output_parser(self):
        parser = StrOutputParser()
        return parser

    def doc2str(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def build_rag_chain(self, retriever, prompt, llm):
        rag_chain = (
                {"context": retriever | self.doc2str, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
        )
        return rag_chain


    def build_conversational_rag_chain(self, llm):
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful assistant that can answer questions about RGUKT.Use the following context to answer the use's question"),
            ("system", "Context: {context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        return question_answer_chain


    def ask_rag(self, question, session_id=None):

        self.setup.set_langsmith_environment()
        self.setup.set_google_environment()
        documents = self.document.load("/Users/anil/Downloads/rag_documents")
        splits = self.document.split(documents)
        # vector_store = store_documents(splits, embedding_model="text-embedding-3-small", model_provider="openai")
        vector_store = self.document.store(splits, embedding_model="sentence-transformers/all-MiniLM-L6-v2", model_provider="huggingface")
        # llm = build_llm(model="google/flan-t5-base", model_provider="huggingface")
        llm = self.build_llm()

        retriever = self.retriever.create(vector_store, 2)
        prompt = self.prompt.create()
        # rag_chain = build_rag_chain(retriever, prompt, llm)

        contextualize_question_prompt = self.prompt.build_contextualize_question_prompt()
        ha_retriever = self.retriever.history_aware_retriever(llm, retriever, contextualize_question_prompt)
        question_answer_chain = self.build_conversational_rag_chain(llm)
        conversational_rag_chain = create_retrieval_chain(ha_retriever, question_answer_chain)


        chat_history = self.db.get_chat_history(session_id)
        response = conversational_rag_chain.invoke({"input": question, "chat_history": chat_history})
        self.db.insert_application_logs(session_id,  question, response["answer"])
        chat_history.extend([HumanMessage(content=question), AIMessage(content=response["answer"])])
        return response["answer"]

class Prompt:
    # Creates chat prompt
    def create(self):
        template = """
            Answer the question based on the following context:
            {context}

            If anybody ask about you, say them that Anil has created you for his personal use.

            Question: {question}

            Answer:
            """
        prompt = ChatPromptTemplate.from_template(template)
        return prompt


    def build_contextualize_question_prompt(self):

        contextualize_qa_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )

        contextualize_question_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_qa_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]
        )
        return contextualize_question_prompt

