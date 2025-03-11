import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import gc

class RAGChatbot:
    def __init__(self, 
                 openai_api_key=None,
                 model_name="gpt-4-turbo",
                 embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
                 faiss_index_path="data/faiss_index.index",
                 chunks_path="data/chunks.npy",
                 TOKENIZERS_PARALLELISM=False):
        """
        Initialize the RAG chatbot with OpenAI's GPT-4 and FAISS index.
        
        Args:
            openai_api_key: Your OpenAI API key
            model_name: The GPT model to use (e.g., "gpt-4-turbo", "gpt-3.5-turbo")
            embedding_model_name: The name of the sentence transformer model for encoding queries
            faiss_index_path: Path to the pre-built FAISS index
            chunks_path: Path to the numpy array of text chunks
        """
        # Set up OpenAI client
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key is None:
                raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=openai_api_key)
        self.model_name = model_name
        
        # Load the FAISS index and text chunks
        print(f"Loading FAISS index from {faiss_index_path}...")
        self.index = faiss.read_index(faiss_index_path)
        
        print(f"Loading text chunks from {chunks_path}...")
        self.chunks = np.load(chunks_path, allow_pickle=True)
        
        # Load the embedding model for query encoding
        print(f"Loading embedding model {embedding_model_name}...")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Run garbage collection
        gc.collect()
        
        print("RAG Chatbot initialization complete!")
    
    def encode_query(self, query):
        """Encode the query using the embedding model"""
        return self.embedding_model.encode([query])[0]
    
    def retrieve_relevant_chunks(self, query_embedding, k=5):
        """Retrieve the k most relevant chunks from the FAISS index"""
        # Ensure the query embedding is in the right shape and type
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Return the retrieved chunks with their relevance scores
        retrieved_chunks = [self.chunks[idx] for idx in indices[0]]
        return retrieved_chunks, distances[0]
    
    def format_messages(self, query, context_chunks, distances=None):
        """Format the messages for the GPT API with the retrieved context"""
        # Join the context chunks into a single context string
        if distances is not None:
            # Sort chunks by relevance (lowest distance is highest relevance)
            sorted_chunks_with_scores = sorted(zip(context_chunks, distances), key=lambda x: x[1])
            # Format chunks with relevance scores
            context_texts = [f"Relevance score: {1/(1+score):.4f}\nChunk: {chunk}" 
                          for chunk, score in sorted_chunks_with_scores]
            context = "\n\n---\n\n".join(context_texts)
        else:
            context = "\n\n---\n\n".join(context_chunks)
        
        # Create messages for the chat completion
        system_message = """You are the official chatbot for Northeastern University's Office of Global Services (OGS).
Your purpose is to assist international students, scholars, and faculty with accurate information about immigration, visa processes, international student services, and university policies.

When responding:
- Use a professional, helpful, and welcoming tone that represents Northeastern University.
- Provide detailed and accurate information based exclusively on the context provided.
- If the information is not available in the context, say: "I don't have that specific information in my knowledge base. Please contact the Office of Global Services directly at ogs@northeastern.edu or call +1-617-373-2310 for assistance."
- Direct students to relevant Northeastern University resources when appropriate.
- Format responses clearly with proper headings and bullet points when presenting multiple pieces of information.
- End your responses with "Is there anything else I can help you with regarding international student services at Northeastern University?"
- Never make up information about visa regulations, deadlines, or university policies not found in the context.
- Use Northeastern University branding in your tone ("We at Northeastern..." or "The Office of Global Services at Northeastern...").
- For urgent or complex matters, recommend that students schedule an appointment with an OGS advisor."""
        
        user_message = f"""Context information: {context}  Question: {query}"""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return messages
    
    def generate_response(self, messages, max_tokens=500):
        """Generate a response from GPT-4 given the formatted messages"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
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
        
        # Step 2: Retrieve relevant chunks
        relevant_chunks, distances = self.retrieve_relevant_chunks(query_embedding)
        
        # Step 3: Format the messages with the context and query
        messages = self.format_messages(query, relevant_chunks, distances)
        
        # Step 4: Generate and return the response
        return self.generate_response(messages)


# Example usage with Streamlit interface
if __name__ == "__main__":
    # Simple CLI interface
    # Set your OpenAI API key
    import os
    os.environ["OPENAI_API_KEY"] = "OPENAI_KEY"  # Replace with your actual API key
    
    try:
        # Initialize the chatbot
        chatbot = RAGChatbot()
        
        print("RAG Chatbot with GPT-4 initialized. Type 'exit' to quit.")
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit", "bye"]:
                break
            
            print("\nThinking...")
            response = chatbot.chat(query)
            print(f"\nChatbot: {response}")
    
    except Exception as e:
        print(f"Error initializing chatbot: {e}")

# Streamlit web interface (uncomment to use)

"""
import streamlit as st

def main():
    st.title("RAG Chatbot with GPT-4")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize the chatbot (only once)
    if "chatbot" not in st.session_state:
        # Set your OpenAI API key
        api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            st.error("OpenAI API key is not set. Please set it in the app secrets or as an environment variable.")
            return
        
        try:
            st.session_state.chatbot = RAGChatbot(openai_api_key=api_key)
            st.success("RAG Chatbot initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing chatbot: {e}")
            return
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input field for new query
    if query := st.chat_input("Ask something about your documents"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(query)
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.chat(query)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
"""
