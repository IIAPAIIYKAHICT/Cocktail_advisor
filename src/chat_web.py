import json
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from llm_integration import query_llm
from vector_db import VectorDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

vector_db = VectorDB()

if vector_db.index.ntotal == 0:
    logger.info("FAISS index is empty. Building the index now...")
    vector_db.prepare_cocktail_index()
    logger.info("Index built successfully!")

llm = ChatOpenAI(temperature=0.7)

class Preferences(BaseModel):
    ingredients: str = Field(description="Comma-separated list of ingredients or an empty string")
    cocktails: str = Field(description="Comma-separated list of cocktails or an empty string")

parser = JsonOutputParser(pydantic_object=Preferences)

preferences_prompt = PromptTemplate(
    template="Analyze the user's message and extract ingredients and/or cocktails that user prefers from that.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Cocktail Advisor Chat</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        #chatbox { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
        #user_input { width: 80%; padding: 10px; }
        #send_button { padding: 10px; }
    </style>
</head>
<body>
    <h1>Cocktail Advisor Chat</h1>
    <div id="chatbox"></div>
    <input type="text" id="user_input" placeholder="Enter your message..."/>
    <button id="send_button">Send</button>

    <script>
        document.getElementById('send_button').onclick = async function() {
            const input = document.getElementById('user_input').value;
            if (input.trim() === "") return;
            const chatbox = document.getElementById('chatbox');
            chatbox.innerHTML += `<p><strong>You:</strong> ${input}</p>`;
            document.getElementById('user_input').value = '';

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: input, user_id: 'user1'})
            });
            const data = await response.json();
            chatbox.innerHTML += `<p><strong>Advisor:</strong> ${data.response}</p>`;
            chatbox.scrollTop = chatbox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_chat():
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message")
    user_id = data.get("user_id", "user1")

    logger.info("Received message from user: %s", user_message)

    # Используем LLM для определения контекста сообщения
    context = determine_message_context(user_message)
    logger.info("Determined message context: %s", context)

    if context == "preferences":
        preferences = extract_preferences_with_llm(user_message)
        logger.info("Extracted preferences: %s", preferences)

        if preferences["ingredients"] or preferences["cocktails"]:
            logger.info("Saving preferences for user %s in FAISS", user_id)
            vector_db.add_user_preferences(user_id, preferences)

    prefs = vector_db.get_user_preferences(user_id)
    logger.info("Current preferences for user %s: %s", user_id, prefs)

    context_text = f"User's favorite ingredients: {', '.join(prefs['ingredients'])}. Favorite cocktails: {', '.join(prefs['cocktails'])}."

    relevant_cocktails = vector_db.search_cocktails(user_message)
    cocktails_info = relevant_cocktails.to_dict(orient="records")

    prompt = f"{context_text}\n\nUser Query: {user_message}\n\nRelevant Cocktails: {json.dumps(cocktails_info, ensure_ascii=False)}\n\nProvide a detailed response based on the above information."

    llm_response = query_llm(prompt)
    logger.info("Generated LLM response: %s", llm_response)

    return JSONResponse(content={"response": llm_response})


def determine_message_context(message: str) -> str:
    logger.info("Determining message context for: %s", message)

    prompt = """
    The user sent the following message:
    "{message}"

    Classify the message into one of the following two categories:
    1. "preferences" - if the message describes the user's favorite ingredients or cocktails, such as:
       - "I love soda, lemon, and peach."
       - "My favorite cocktail is Mojito."
    2. "query" - if the message contains a question or request for information, such as:
       - "What cocktails can I make with lime and soda?"
       - "Recommend 5 cocktails that contain my favorite ingredients."

    Respond with either "preferences" or "query".
    """.strip()

    response = query_llm(prompt.format(message=message))
    context = response.strip().lower()
    logger.info("Message context determined: %s", context)
    return context


def extract_preferences_with_llm(message: str) -> dict:
    logger.info("Extracting preferences using LLM for message: %s", message)
    try:
        # Выполняем запрос через цепочку
        query = {"query": message}
        preferences_result = (preferences_prompt | llm | parser).invoke(query)
        logger.info("Raw preferences result: %s", preferences_result)

        # Извлекаем значения из словаря
        ingredients = preferences_result.get("ingredients", "")
        cocktails = preferences_result.get("cocktails", "")

        # Преобразуем строки в списки
        return {
            "ingredients": [i.strip().lower() for i in ingredients.split(",") if i.strip()],
            "cocktails": [c.strip() for c in cocktails.split(",") if c.strip()],
        }
    except Exception as e:
        logger.error("Error extracting preferences: %s", e)
        return {"ingredients": [], "cocktails": []}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
