import os

if not os.getenv('ENV_STATUS') == '1':
    import utils  # This loads vars, do not remove
from model.claude import *


def run_rag_claude(rebuild=False, index_name="claude_index", chunked_dir=''):
    """
    Run the RAG Chat System with the specified parameters.

    Args:
        rebuild (bool): Force rebuild the index if True
        index_name (str): Name of the index directory
        chunked_dir (str): Directory containing chunked HTML files
    """

    if not chunked_dir:
        chunked_dir = os.getenv('CHUNKDATA_DIR')

    # Check if we need to build/rebuild the index
    if rebuild or not index_exists(index_name):
        # Read all chunks from the HTML files
        print("Reading chunked HTML files...")
        chunks = read_chunked_html(chunked_dir)
        print(f"Found {len(chunks)} chunks across all files")

        # Build the RAG index
        print("Building RAG index with MPS acceleration...")
        index = build_rag_index(chunks, index_name=index_name)
        print("Index built successfully!")
    else:
        print(f"Using existing index from {index_name}")

    # Create chat engine
    chat_engine = create_chat_engine(index_name=index_name)

    # Interactive chat loop
    print("\nRAG Chat System Ready! Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break

        try:
            response = chat_engine.chat(user_input)
            print(f"\nAssistant: {response.response}")
        except Exception as e:
            print("ERROR: ", e)
