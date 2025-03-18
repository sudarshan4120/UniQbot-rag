import os
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

# Folder containing the chunked HTML files (adjust if needed)
chunked_html_folder = "/Users/sudarshanp/Desktop/shreya_bot/data/chunks"
output_dir = "/Users/sudarshanp/Desktop/shreya_bot/data"  # Path for storing the FAISS index

# Function to load the chunked HTML content
def load_chunked_html_files(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.html')]
    chunks = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            # Each paragraph in the chunked HTML is considered a separate chunk
            chunks.extend([p.get_text() for p in soup.find_all('p')])
    return chunks

# Load chunked HTML files
print(f"Loading chunks from {chunked_html_folder}...")
all_chunks = load_chunked_html_files(chunked_html_folder)
print(f"Loaded {len(all_chunks)} chunks.")

# Load BERT model and tokenizer
print("Loading model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Generate embeddings for all chunks
def get_embeddings(text_chunks, batch_size=16):  # Add batch_size parameter
    embeddings = []
    total_batches = (len(text_chunks) + batch_size - 1) // batch_size
    
    for i in range(0, len(text_chunks), batch_size):
        batch = text_chunks[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{total_batches}")
        encoded_input = tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model(**encoded_input)
        embeddings.append(model_output.pooler_output.to(torch.float16).cpu().numpy())  # Lower precision for less memory
    return np.vstack(embeddings)

print(f"Generating embeddings for {len(all_chunks)} chunks...")
embeddings = get_embeddings(all_chunks)
print(f"Generated embeddings with shape: {embeddings.shape}")

# Store in FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings, dtype='float32'))

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Save FAISS index
index_path = os.path.join(output_dir, "faiss_index-shreya.index")
faiss.write_index(index, index_path)

print(f"Embeddings stored successfully in FAISS at {index_path}")

# Example query
query = "where is Boston University"
encoded_query = tokenizer(query, padding=True, truncation=True, return_tensors='pt')

# Generate the query embedding
with torch.no_grad():
    query_embedding = model(**encoded_query).pooler_output[0].numpy()

# FAISS search
D, I = index.search(np.array([query_embedding], dtype='float32'), k=3)
print("Top 3 closest chunks:", I)  # Top 3 closest chunks

# Display the content of the top relevant chunks
print("\nSearch results for query:", query)
print("=" * 50)
for i, idx in enumerate(I[0]):
    if idx != -1:
        print(f"Result {i+1} (Score: {D[0][i]:.4f})")
        print(f"Chunk ID: {idx}")
        print(f"Content: {all_chunks[idx]}")
        print("-" * 50)
