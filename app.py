import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Create FastAPI app
app = FastAPI(title="AI Study Assistant Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class GenerateRequest(BaseModel):
    topic: str
    feature: str  # notes, summary, quiz, doubt

# Prompt templates
def build_prompt(topic: str, feature: str) -> str:
    feature = feature.lower()

    prompts = {
        "notes": f"""
Create concise but high-quality study notes on "{topic}" for a Class 11/12 and JEE student.
Include:
- Definition / introduction
- Key concepts
- Important formulas
- Short tricks or tips
- Exam-focused points
""",
        "summary": f"""
Write a short and clear summary of "{topic}" suitable for quick revision.
""",
        "quiz": f"""
Generate 10 mixed questions (MCQ and short-answer) on "{topic}" with answers.
""",
        "doubt": f"""
Explain "{topic}" in a simple and intuitive way for a student.
"""
    }

    return prompts.get(feature, f"Explain {topic} in detail.")

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "AI Study Assistant Backend is running!"
    }

# Generate endpoint
@app.post("/generate")
def generate(request: GenerateRequest):
    try:
        prompt = build_prompt(request.topic, request.feature)
        response = model.generate_content(prompt)

        return {
            "success": True,
            "topic": request.topic,
            "feature": request.feature,
            "result": response.text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
