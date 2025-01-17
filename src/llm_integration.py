from langchain_openai import ChatOpenAI
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=OPENAI_API_KEY)

def query_llm(prompt: str) -> str:
    """
    Генерация ответа на основе запроса через LangChain.
    """
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Ошибка генерации ответа: {str(e)}"