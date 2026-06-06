def build_vectorstore(regulation_paths: List[str]):
    all_docs = []

    for file_path in regulation_paths:
        all_docs.extend(load_file(file_path))

    if not all_docs:
        raise ValueError("규정/법령 문서가 없습니다.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(all_docs)

    if not chunks:
        raise ValueError("규정/법령 문서에서 텍스트를 추출하지 못했습니다.")

    embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embedding,
    )

    return vectorstore, len(all_docs), len(chunks)