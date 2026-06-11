import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=0,
    )