import uvicorn
from fastapi import FastAPI

from langchain_rag.controller import rag_router

if __name__ == "__main__":
    app = FastAPI()

    app.include_router(rag_router)

    uvicorn.run(app, host="0.0.0.0", port=8080)