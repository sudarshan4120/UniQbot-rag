import os
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from llama_index.core.text_splitter import TokenTextSplitter

# Ensure required NLTK package is downloaded
nltk.download('punkt')

def extract_text_from_html(cleaned_html):
    """
    Extracts clean text from HTML content.
    """
    soup = BeautifulSoup(cleaned_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def sentence_based_chunking(text):
    """
    Primary Chunking: Splits text into meaningful sentences using NLTK.
    """
    return sent_tokenize(text)

def token_based_chunking(sentences, chunk_size=256, chunk_overlap=30):
    """
    Secondary Chunking: If sentences exceed the token limit, apply token-based chunking.
    """
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    
    for sentence in sentences:
        if len(sentence.split()) > chunk_size:  # Check if sentence exceeds token limit
            chunks.extend(text_splitter.split_text(sentence))
        else:
            chunks.append(sentence)
    
    return chunks

def process_files(input_dir, output_dir):
    """
    Reads cleaned HTML files, extracts text, applies chunking, and saves results in HTML format.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"chunked_{filename}")  # Save as .html
            
            with open(input_path, 'r', encoding='utf-8') as file:
                cleaned_html = file.read()
            
            # Extract text
            text = extract_text_from_html(cleaned_html)
            
            # Apply primary chunking
            sentence_chunks = sentence_based_chunking(text)
            
            # Apply secondary chunking where necessary
            final_chunks = token_based_chunking(sentence_chunks)
            
            # Format chunks as HTML
            html_output = "<html><body>\n"
            html_output += "\n<hr>\n".join(f"<p>{chunk.strip()}</p>" for chunk in final_chunks if chunk.strip())
            html_output += "\n</body></html>"
            
            # Save chunked data as HTML
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(html_output)
            
            print(f"Chunked {filename} successfully!")
    
    print("All cleaned HTML files have been chunked!")

if __name__ == "__main__":
    input_dir = '/Users/shreya/Desktop/Project1/Data/Cleaned'  # Path for cleaned HTML files
    output_dir = '/Users/shreya/Desktop/Project1/Data/Chunked'  # Path for storing chunked HTML files
    process_files(input_dir, output_dir)
