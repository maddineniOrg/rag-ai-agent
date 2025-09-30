import uvicorn
from fastapi import FastAPI

if __name__ == '__main__':
    from telegram_bot.controller import telegram_bot_router

    app = FastAPI()
    app.include_router(telegram_bot_router)

    uvicorn.run(app, host="0.0.0.0", port=8080)