import os

from dotenv import load_dotenv


class Setup:
    # Setting Langsmith Environment
    def set_langsmith_environment(self):
        """

        :return:
        """
        load_dotenv()
        os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
        os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
        os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

    # Setting Google API key
    def set_google_environment(self):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")