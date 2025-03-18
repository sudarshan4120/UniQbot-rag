import os
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
import torch
import chromadb
import faiss
import numpy as np

# Folder containing the HTML files
html_folder = "data/cleaned_html/"

# Function to load and parse all HTML files in the folder
def load_html_files_with_links(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.html')]
    results = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            # Extract text
            text = soup.get_text()
            # Extract links with their text and URLs
            links = []
            for a_tag in soup.find_all('a', href=True):
                links.append({
                    'text': a_tag.get_text(),
                    'href': a_tag['href']
                })
            results.append({
                'filename': os.path.basename(file),
                'text': text,
                'links': links
            })
    return results

# Function to chunk the text
def chunk_text(text, max_length=512):
    words = text.split()
    return [' '.join(words[i:i+max_length]) for i in range(0, len(words), max_length)]

# Load HTML files and extract text from each
html_texts = load_html_files_with_links(html_folder)

# Chunk all texts from all HTML files
all_chunks = []
for html_item in html_texts:
    # Access the 'text' field of the dictionary
    text_content = html_item['text']
    chunks = chunk_text(text_content)
    all_chunks.extend(chunks)  # Append all chunks

# Load BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Generate embeddings for all chunks
def get_embeddings(text_chunks):
    encoded_input = tokenizer(text_chunks, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    return model_output.pooler_output.numpy()

embeddings = get_embeddings(all_chunks)

# Store in ChromaDB
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="html_embeddings")
for idx, emb in enumerate(embeddings):
    collection.add(embeddings=emb.tolist(), metadatas={"chunk_id": idx}, ids=str(idx))

# Store in FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings, dtype='float32'))

# Save FAISS index
faiss.write_index(index, "data/faiss_index.index")

print("Embeddings stored successfully in ChromaDB and FAISS.")

# Example query
query = "Link for getting I-20 form?"  # Example query
encoded_query = tokenizer(query, padding=True, truncation=True, return_tensors='pt')

# Generate the query embedding
with torch.no_grad():
    query_embedding = model(**encoded_query).pooler_output[0].numpy()  # Extract the pooled output

# Now it's ready for FAISS search
D, I = index.search(np.array([query_embedding], dtype='float32'), k=3)
print(I)  # Top 5 closest chunks

# Display the content of the top 5 most relevant chunks
for idx in I[0]:
    if idx != -1:
        print(f"Chunk ID: {idx}, Content: {all_chunks[idx]}")
