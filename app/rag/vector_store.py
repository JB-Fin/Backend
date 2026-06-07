import os
from pathlib import Path
from typing import List

from fastapi import HTTPException, status
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from app.rag.document_loader import load_file

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

def build_vectorstore(regulation_paths: List[str]):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY가 설정되지 않았습니다.",
        )

    all_docs = []

    for file_path in regulation_paths:
        path = Path(file_path)

        if not path.exists():
            continue

        all_docs.extend(load_file(str(path)))

    if not all_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="규정/법령 문서가 없습니다.",
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(all_docs)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="규정/법령 문서에서 텍스트를 추출하지 못했습니다.",
        )

    embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embedding,
    )

    return vectorstore, len(all_docs), len(chunks)