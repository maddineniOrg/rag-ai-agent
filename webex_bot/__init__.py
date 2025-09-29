import uvicorn
from fastapi import FastAPI

import webex_bot
from webex_bot.controller import webex_bot_router

if __name__ == "__main__":

    app = FastAPI()
    app.include_router(webex_bot_router)

    uvicorn.run(app, host="0.0.0.0", port=8080)