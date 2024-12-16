from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import numpy as np
import requests
import faiss
from mixedbread_ai.client import MixedbreadAI

MIXEDBREAD_AI_API_KEY = "emb_defb9cfe82a984980d32450c5cd2f298806581d99d7e5237"

# Constants
EMBEDDING_SERVICE_URL = r"http://localhost:11434/api/embeddings"
MERGED_DATA_PATH_1 = r"RAG/ais328dq/embd.json"
MERGED_DATA_PATH_2 = r"RAG/ova/embd.json"

with open(MERGED_DATA_PATH_1, 'r') as file:
    merged_data_1 = json.load(file)
with open(MERGED_DATA_PATH_2, 'r') as file:
    merged_data_2 = json.load(file)

ls = [merged_data_1, merged_data_2]

# Initialize FastAPI app
app = FastAPI()

# Request model
class QueryRequest(BaseModel):
    query: str
    tp: int

# Response model
class ContextItem(BaseModel):
    title: str
    contents: str

# Helper function to call the embedding service
def embed(chunk: str) -> np.ndarray:
    """Generate an embedding for the input text using the embedding service."""
    mxbai = MixedbreadAI(api_key=MIXEDBREAD_AI_API_KEY)

    embeddings = mxbai.embeddings(
        model="mixedbread-ai/mxbai-embed-large-v1",
        input=[chunk]
    )
    return np.array(embeddings.data[0].embedding)


# Helper function to compute the query embedding
def compute_query_embedding(query: str) -> np.ndarray:
    """Compute the embedding for the query."""
    return embed(query)

# Main RAG search logic
def rag_search(
    query: str, 
    k: int, 
    tp: int, 
):
    # Validate input parameters
    if not (0 <= tp <= len(ls)-1):
        raise HTTPException(status_code=400, detail=f"Invalid 'tp' value: {tp}")
    
    # Compute query embedding efficiently
    query_embedding = np.array(compute_query_embedding(query), dtype=np.float32)
    
    # Select and prepare dataset
    merged_data = ls[tp]
    
    # Use pre-computed embeddings to avoid repeated computation
    passage_embeddings = np.stack([
        entry["embedding"] for entry in merged_data
    ]).astype(np.float32)
    
    # Create FAISS index with more efficient search method
    index = faiss.IndexFlatIP(passage_embeddings.shape[1])  # Inner product (cosine) similarity
    index.add(passage_embeddings)
    
    # Efficient search with numpy operations
    distances, indices = index.search(
        query_embedding.reshape(1, -1), 
        min(k, len(merged_data))
    )
    
    # Retrieve top passages with error handling
    top_passages = [
        merged_data[idx] 
        for idx in indices[0] 
        if 0 <= idx < len(merged_data)
    ]
    
    # Optimized result formatting
    return [
        {
            "title": "context", 
            "contents": passage["text"]
        } for passage in top_passages
    ]

# Endpoint for retrieving context items
@app.post("/retrieve", response_model=List[ContextItem])
async def retrieve_context_items(request: QueryRequest):
    """Retrieve the top K context items for a given query."""
    query = request.query.strip().lower()  # Preprocess query
    print("query=", query)
    print("tp=", request.tp)
    try:
        return rag_search(query, k=10, tp=request.tp)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
