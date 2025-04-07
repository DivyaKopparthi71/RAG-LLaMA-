# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from fastapi.middleware.cors import CORSMiddleware
import os
import re

app = FastAPI(title="BCPA Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load FAISS index
FAISS_INDEX_PATH = "index"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if not os.path.exists(FAISS_INDEX_PATH):
    raise Exception("FAISS index folder not found!")

retriever = FAISS.load_local(FAISS_INDEX_PATH, embeddings=embedding_model, allow_dangerous_deserialization=True).as_retriever(search_kwargs={"k": 5})
llm = OllamaLLM(model="llama3", temperature=0.7, max_tokens=200)

rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

class QueryRequest(BaseModel):
    question: str

def clean_answer(answer: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[\{\}]", "", answer)).strip()

@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        result = rag_chain.invoke(request.question)
        return {"answer": clean_answer(str(result))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
