import os

if not os.getenv('ENV_STATUS') == '1':
    import utils  # This loads vars, do not remove

from bs4 import BeautifulSoup
from llama_index.core import Document, Settings
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.anthropic import Anthropic
# Use the correct import for HuggingFace embeddings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def read_chunked_html(chunked_dir):
    """
    Reads chunked HTML files and extracts the individual chunks.
    Returns a list of tuples containing (filename, chunk_text).
    """
    all_chunks = []

    for filename in os.listdir(chunked_dir):
        if filename.startswith('chunked_') and filename.endswith('.html'):
            file_path = os.path.join(chunked_dir, filename)
            original_filename = filename.replace('chunked_', '', 1)

            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract each chunk (paragraph) from the HTML
            chunk_elements = soup.find_all('p')

            for chunk in chunk_elements:
                chunk_text = chunk.get_text(strip=True)
                if chunk_text:  # Only add non-empty chunks
                    # Store as tuple of (source_file, chunk_text)
                    all_chunks.append((original_filename, chunk_text))

    return all_chunks


def build_rag_index(chunks, index_name="my_rag_index"):
    """
    Builds a RAG index using LlamaIndex from the extracted chunks.
    Uses Claude API for generation and MPS for GPU acceleration.
    """
    # Initialize Claude LLM
    llm = Anthropic(
        api_key="",
        model="claude-3-haiku-20240307",
        temperature=0.2,
    )

    # Use HuggingFace embeddings with MPS acceleration
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-en",
        device="mps",  # Use Metal Performance Shaders on Apple Silicon
        embed_batch_size=16  # Optimize batch size for MPS
    )

    # Configure global settings for LLM and embedding model
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Create Documents for LlamaIndex
    documents = []

    for source_file, chunk_text in chunks:
        # Create a Document object with metadata
        doc = Document(
            text=chunk_text,
            metadata={
                "source": source_file,
            }
        )
        documents.append(doc)

    # Build the index
    print("Indexing documents with MPS acceleration...")
    index = VectorStoreIndex.from_documents(
        documents,
        show_progress=True  # Show progress bar for indexing
    )

    # Save the index for later use
    index.storage_context.persist(persist_dir=index_name)

    return index


def create_chat_engine(index_name="my_rag_index"):
    """
    Create a chat engine from the saved index using Claude API.
    """
    # Initialize Claude LLM
    llm = Anthropic(
        api_key="",
        model="claude-3-haiku-20240307",
        temperature=0.2,
    )

    # Use HuggingFace embeddings with MPS acceleration
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-en",
        device="mps",  # Use Metal Performance Shaders on Apple Silicon
        embed_batch_size=16  # Optimize batch size for MPS
    )

    # Configure global settings for LLM and embedding model
    Settings.llm = llm
    Settings.embed_model = embed_model

    # Load the index
    storage_context = StorageContext.from_defaults(persist_dir=index_name)
    index = load_index_from_storage(storage_context)

    # Create memory buffer for chat history
    memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

    # Create chat engine with memory
    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=memory,
        verbose=True,
    )

    return chat_engine


# Example usage
if __name__ == "__main__":
    chunked_dir = '/Users/nmnsnghl/Work/Github/UniQbot-rag/data/chunked'

    # Read all chunks from the HTML files
    print("Reading chunked HTML files...")
    chunks = read_chunked_html(chunked_dir)
    print(f"Found {len(chunks)} chunks across all files")

    # Build the RAG index
    print("Building RAG index with MPS acceleration...")
    index = build_rag_index(chunks)
    print("Index built successfully!")

    # Create chat engine
    chat_engine = create_chat_engine()

    # Interactive chat loop
    print("\nRAG Chat System Ready! Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break

        response = chat_engine.chat(user_input)
        print(f"\nAssistant: {response.response}")