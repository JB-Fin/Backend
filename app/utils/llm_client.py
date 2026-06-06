import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=0,
    )