from fastapi import APIRouter, HTTPException, Depends
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
from typing import Dict
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

router = APIRouter()

class ChatRequest(BaseModel):
    user_message: str
    username: str

# Function to scrape web for period-related information
def scrape_period_info(query: str) -> str:
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return "Sorry, I couldn't fetch information at this time."
    soup = BeautifulSoup(response.text, "html.parser")
    snippets = soup.find_all("span")
    for snippet in snippets:
        if snippet.text.strip():
            return snippet.text.strip()
    return "No relevant information found."

@router.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        user_input = request.user_message.lower()
        if "when is my next period" in user_input:
            return {"response": f"You can check your predicted period date on the dashboard."}
        elif "symptoms of period" in user_input:
            scraped_info = scrape_period_info("common period symptoms")
            return {"response": scraped_info}
        else:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": request.user_message}]
            )
            return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
