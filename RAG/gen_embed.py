import json
import random
import requests
import json

# Ollama API URL for embeddings
doc_path=r"RAG\ova\ova5640_doc.json"
write_path=r"RAG\ova\embd.json"
url = "http://localhost:11434/api/embeddings"
def embed(chunk):
    data = {
    "model": "mxbai-embed-large:latest",  # Model to use
    "prompt": chunk  # Text to embed
}
    response = requests.post(url, json=data)
    result = response.json()
    embedding = result.get("embedding", [])
    return embedding

def generate_embedding(text):

    return embed(text)  

# Read JSON data from a file
with open(doc_path, 'r') as file:
    data = json.load(file)
with open(write_path, 'w') as file:
    json.dump(data, file, indent=2)

# Process each item in the JSON list and add the "embedding" field
for item in data:
    text = item["text"]
    item["embedding"] = generate_embedding(text)

# Write the updated JSON data back to a new file
with open(write_path, 'w') as file:
    json.dump(data, file, indent=2)


print("Embeddings added and data saved to 'output.json'.")
