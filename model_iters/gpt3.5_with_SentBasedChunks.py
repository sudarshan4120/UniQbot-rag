import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import gc
import os
import tiktoken  
from bs4 import BeautifulSoup
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class RAGChatbot:
    def __init__(self, 
                 openai_api_key=None,
                 model_name="gpt-3.5-turbo",
                 embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
                 faiss_index_path="/Users/sudarshanp/Desktop/shreya_bot/data/faiss_index-shreya.index",
                 chunks_folder="/Users/sudarshanp/Desktop/shreya_bot/data/chunks",
                 max_chunks=5,  # Default number of chunks to retrieve
                 max_context_tokens=12000):  # Reserve tokens for context
        """
        Initialize the RAG chatbot with OpenAI's GPT and FAISS index.
        
        Args:
            openai_api_key: Your OpenAI API key
            model_name: The GPT model to use ("gpt-3.5-turbo")
            embedding_model_name: The name of the sentence transformer model for encoding queries
            faiss_index_path: Path to the pre-built FAISS index
            chunks_folder: Path to the folder containing chunked HTML files
            max_chunks: Maximum number of chunks to retrieve
            max_context_tokens: Maximum tokens to use for context
        """
        # Set up OpenAI client
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key is None:
                raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=openai_api_key)
        self.model_name = model_name
        self.max_chunks = max_chunks
        self.max_context_tokens = max_context_tokens
        
        # to calculate token counts
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        # Load the FAISS index
        print(f"Loading FAISS index from {faiss_index_path}...")
        self.index = faiss.read_index(faiss_index_path)
        
        # Load the chunks from HTML files
        print(f"Loading text chunks from {chunks_folder}...")
        # Load chunked HTML files
        files = [os.path.join(chunks_folder, f) for f in os.listdir(chunks_folder)]
        self.chunks = []
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                # Each paragraph in the chunked HTML is considered a separate chunk
                self.chunks.extend([p.get_text() for p in soup.find_all('p')])
        
        print(f"Loaded {len(self.chunks)} chunks.")
        
        # Load the embedding model for query encoding
        print(f"Loading embedding model {embedding_model_name}...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Run garbage collection
        gc.collect()
        
        print("RAG Chatbot initialization complete!")
    
    def encode_query(self, query):
        """Encode the query using the embedding model"""
        return self.embedding_model.encode([query])[0]
    
    def num_tokens(self, text):
        """Calculate the number of tokens in a text string"""
        return len(self.tokenizer.encode(text))
    
    def retrieve_relevant_chunks(self, query_embedding, k=None):
        """Retrieve the k most relevant chunks from the FAISS index"""
        if k is None:
            k = self.max_chunks
            
        # Retrieve more chunks than we might need (we'll filter later)
        k_search = min(k * 3, len(self.chunks))  # Get 3x more candidates
        
        # Ensure the query embedding is in the right shape and type
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k_search)
        
        # Return the retrieved chunks with their relevance scores
        retrieved_chunks = [self.chunks[idx] for idx in indices[0]]
        return retrieved_chunks, distances[0]
    
    def filter_chunks_by_relevance_and_tokens(self, chunks, distances, similarity_threshold=0.6):
        """Filter chunks by relevance and token count"""
        # Convert distances to similarity scores (assuming L2 distance)
        # For L2 distance, smaller values are more similar
        max_distance = max(distances)
        similarity_scores = [1 - (dist / max_distance) for dist in distances]
        
        # Filter by similarity threshold
        filtered_chunks = []
        filtered_distances = []
        
        # First filter by similarity
        for chunk, dist, sim in zip(chunks, distances, similarity_scores):
            if sim >= similarity_threshold:
                filtered_chunks.append(chunk)
                filtered_distances.append(dist)
        
        # Then filter by token count
        final_chunks = []
        final_distances = []
        total_tokens = 0
        
        # Sort by distance (ascending) so more relevant chunks come first
        sorted_items = sorted(zip(filtered_chunks, filtered_distances), key=lambda x: x[1])
        
        for chunk, dist in sorted_items:
            chunk_tokens = self.num_tokens(chunk)
            if total_tokens + chunk_tokens <= self.max_context_tokens:
                final_chunks.append(chunk)
                final_distances.append(dist)
                total_tokens += chunk_tokens
            else:
                # We've reached the token limit
                break
                
        print(f"Selected {len(final_chunks)} chunks totaling {total_tokens} tokens")
        return final_chunks, final_distances
    
    def format_messages(self, query, context_chunks, distances=None):
        """Format the messages for the GPT API with the retrieved context"""
        # Join the context chunks into a single context string
        if distances is not None and len(distances) > 0:
            # Sort chunks by relevance (lowest distance is highest relevance)
            sorted_chunks_with_scores = sorted(zip(context_chunks, distances), key=lambda x: x[1])
            # Format chunks with relevance scores
            context_texts = [f"Relevance score: {1/(1+score):.4f}\nChunk: {chunk}" 
                          for chunk, score in sorted_chunks_with_scores]
            context = "\n\n---\n\n".join(context_texts)
        else:
            context = "\n\n---\n\n".join(context_chunks)
        
        # Create messages for the chat completion
        system_message = """You are the official chatbot for Northeastern University's Office of Global Services (OGS). Your role is to assist international students, scholars, and faculty with accurate information about immigration, visa processes, international student services, and university policies.
                    When responding:
                    - Use Northeastern branding ("We at Northeastern..." or "The Office of Global Services at Northeastern...").
                    - For complex matters, recommend scheduling an appointment with an OGS advisor.
                    - Provide only accurate visa/immigration information from the knowledge base.
                    - If unsure, advise contacting OGS at ogs@northeastern.edu or +1-617-373-2310.
                    - Only give answers for Northeastern university!
                    - End responses with: "Is there anything else I can help you with?" """
        
        user_message = f"""Context information: {context}  Question: {query}"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Calculate and log total tokens
        total_tokens = self.num_tokens(system_message) + self.num_tokens(user_message)
        print(f"Total tokens in prompt: {total_tokens}")
        
        return messages
    
    def generate_response(self, messages, max_tokens=300):
        """Generate a response from GPT given the formatted messages"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.9,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"Error generating response: {str(e)}"
    
    def chat(self, query):
        """Process a query through the full RAG pipeline"""
        # Step 1: Encode the query
        query_embedding = self.encode_query(query)
        
        # Step 2: Retrieve more relevant chunks than we'll ultimately use
        candidate_chunks, distances = self.retrieve_relevant_chunks(query_embedding, k=self.max_chunks * 3)
        
        # Step 3: Filter chunks by relevance and token count
        filtered_chunks, filtered_distances = self.filter_chunks_by_relevance_and_tokens(
            candidate_chunks, distances
        )
        
        # Step 4: Format the messages with the context and query
        messages = self.format_messages(query, filtered_chunks, filtered_distances)
        
        # Step 5: Generate and return the response
        return self.generate_response(messages)


# Example usage with Streamlit interface
if __name__ == "__main__":
    # Simple CLI interface
    # Set your OpenAI API key
    import os
    os.environ["OPENAI_API_KEY"] = "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"  # Replace with your actual API key
    
    try:
        # Initialize the chatbot with controlled context size
        chatbot = RAGChatbot(
            max_chunks=5,  # Start with retrieving 5 chunks
            max_context_tokens=10000  # Reserve ~10K tokens for context (leaving ~6K for system prompt and completion)
        )
        
        print("RAG Chatbot initialized. Type 'exit' to quit.")
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit", "bye"]:
                break
            
            print("\nThinking...")
            response = chatbot.chat(query)
            print(f"\nChatbot: {response}")
    
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
