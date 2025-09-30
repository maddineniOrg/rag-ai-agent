# This is a sample Python script.
# from pyngrok import ngrok
import nest_asyncio
import uvicorn
from fastapi import FastAPI

from langchain_rag import rag_router
from telegram_bot.controller import telegram_bot_router
from webex_bot.controller import webex_bot_router


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    nest_asyncio.apply()


    app = FastAPI()
    app.include_router(webex_bot_router)
    app.include_router(rag_router)
    app.include_router(telegram_bot_router)



    # # Expose port 8000 using ngrok
    # # Set your authtoken here
    # ngrok.set_auth_token("338nLUMa2LlNfhKQPvijWKGTOk4_4RDy3FXz6nxPhJVvF5xVs")
    # public_url = ngrok.connect(8000)
    # print("Public URL:", public_url)

    # Run the app
    uvicorn.run(app, host="0.0.0.0", port=8080)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
