import os
import google.generativeai as genai
from google.oauth2 import service_account
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Load service account credentials
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Initialize Gemini API
genai.configure(credentials=credentials)

# Load and process text data
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def split_text(text, chunk_size=500):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Create vector store using FAISS
def create_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store

# Load and prepare data
text = load_text('C:/Users/DELL/monthly-buddy/server/common_faqs.txt')
text_chunks = split_text(text)
vector_store = create_vector_store(text_chunks)

# Define request and response models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# Function to generate responses using Gemini API
def get_gemini_response(query):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(query)
    return response.text if response else "I couldn't generate an answer."

# chatbot router
router = APIRouter()

# Define FastAPI route
@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    try:
        # Retrieve relevant text from FAISS
        relevant_texts = vector_store.similarity_search(request.question, k=3)
        context = "\n".join([doc.page_content for doc in relevant_texts])

        # Use Gemini API to generate response
        final_prompt = f"Based on the following information, answer the question:\n\n{context}\n\nQuestion: {request.question}"
        answer = get_gemini_response(final_prompt)
        
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app with: uvicorn app:app --reload
