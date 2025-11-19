import os
from pymongo import MongoClient
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Configuration
# -------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "rag_db"
COLLECTION_NAME = "embeddings"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# -------------------------
# Embedding Model
# -------------------------
# Ensure you have run: ollama pull nomic-embed-text
embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
)

# -------------------------
# Process PDF → Chunk → Embed
# -------------------------
def process_document(file, filename):
    pdf_reader = PdfReader(file)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    all_docs = []

    for page_num, page in enumerate(pdf_reader.pages, start=1):
        extracted = page.extract_text()
        if not extracted:
            continue

        chunks = text_splitter.split_text(extracted)
        for chunk in chunks:
            # Clean metadata is crucial
            all_docs.append(
                Document(page_content=chunk, metadata={"source": filename, "page": page_num})
            )

    if all_docs:
        # Batch insert is more efficient
        vector_store.add_documents(all_docs)
        print(f"Uploaded {len(all_docs)} chunks to MongoDB for {filename}")
        return len(all_docs)
    
    return 0

# -------------------------
# Helper: Format Docs to String
# -------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -------------------------
# Query System
# -------------------------
def get_answer(query):
    # Ensure you have run: ollama pull llama3.1
    llm = ChatOllama(model="llama3.1", temperature=0)
    
    retriever = vector_store.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": 4}
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a helpful assistant. Use the following context to answer the question.
        If the answer is not in the context, say you don't know.
        
        Context:
        {context}
        
        Question: {question}
        Answer:"""
    )

    # FIXED: Using RunnablePassthrough to handle formatting correctly
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        # Get Answer
        answer = rag_chain.invoke(query)
        
        # Get Sources separately for display
        source_docs = retriever.invoke(query)
        sources = list(set([d.metadata.get("source", "Unknown") for d in source_docs]))
        
        return {"answer": answer, "sources": sources}
    except Exception as e:
        print(f"RAG Error: {e}")
        return {"answer": "Error processing your request. Is Ollama running?", "sources": []}

# -------------------------
# List All Uploaded Document Names
# -------------------------
def get_all_documents():
    try:
        # Retrieves unique filenames from metadata
        docs = collection.distinct("metadata.source")
        return docs if docs else []
    except Exception as e:
        print(f"DB Error: {e}")
        return []