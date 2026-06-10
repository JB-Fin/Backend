# import os
# from pathlib import Path
# from typing import List

# from fastapi import HTTPException, status
# from langchain_openai import OpenAIEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS

# from app.rag.document_loader import load_file

# EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# CHUNK_SIZE = 600
# CHUNK_OVERLAP = 100

# def build_vectorstore(regulation_paths: List[str]):
#     if not os.getenv("OPENAI_API_KEY"):
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="OPENAI_API_KEY가 설정되지 않았습니다.",
#         )

#     all_docs = []

#     for file_path in regulation_paths:
#         path = Path(file_path)

#         if not path.exists():
#             continue

#         all_docs.extend(load_file(str(path)))

#     if not all_docs:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="규정/법령 문서가 없습니다.",
#         )

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=CHUNK_SIZE,
#         chunk_overlap=CHUNK_OVERLAP,
#         separators=["\n\n", "\n", ".", " ", ""],
#     )

#     chunks = splitter.split_documents(all_docs)

#     if not chunks:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="규정/법령 문서에서 텍스트를 추출하지 못했습니다.",
#         )

#     embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)

#     vectorstore = FAISS.from_documents(
#         documents=chunks,
#         embedding=embedding,
#     )

#     return vectorstore, len(all_docs), len(chunks)

import logging
from typing import List

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from app.rag.document_loader import load_file

logger = logging.getLogger("vector_store")

EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100


def build_vectorstore(regulation_paths: List[str]):
    logger.info("[VECTOR] build_vectorstore 시작")
    logger.info(f"[VECTOR] regulation_paths={regulation_paths}")

    all_docs = []

    for file_path in regulation_paths:
        logger.info(f"[VECTOR] 규정 파일 로드 시작: {file_path}")
        docs = load_file(file_path)
        logger.info(f"[VECTOR] 규정 파일 로드 완료: {file_path}, docs={len(docs)}")
        all_docs.extend(docs)

    logger.info(f"[VECTOR] 전체 docs 수: {len(all_docs)}")

    if not all_docs:
        raise ValueError("규정/법령 문서가 없습니다.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    logger.info("[VECTOR] chunk split 시작")
    chunks = splitter.split_documents(all_docs)
    logger.info(f"[VECTOR] chunk split 완료: chunks={len(chunks)}")

    if not chunks:
        raise ValueError("규정/법령 문서에서 텍스트를 추출하지 못했습니다.")

    logger.info("[VECTOR] OpenAIEmbeddings 객체 생성 시작")
    embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    logger.info("[VECTOR] OpenAIEmbeddings 객체 생성 완료")

    logger.info("[VECTOR] FAISS.from_documents 시작")
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embedding,
    )
    logger.info("[VECTOR] FAISS.from_documents 완료")

    return vectorstore, len(all_docs), len(chunks)