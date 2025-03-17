import os
#from extract import run_scraper
from clean import process_cleaning
from chunk_2 import process_files

def main():
    # Define paths
    raw_html_dir = '/Users/shreya/Desktop/Project1/Data/raw'
    cleaned_html_dir = '/Users/shreya/Desktop/Project1/Data/Cleaned'
    chunked_output_dir = '/Users/shreya/Desktop/Project1/Data/Chunked'
    
    # Define base URL for scraping
    base_url = "https://international.northeastern.edu/ogs/"  # Change this to actual website
    
    #print("Starting web scraping...")
    #run_scraper(base_url, raw_html_dir)
    
    print("Cleaning extracted HTML files...")
    process_cleaning(raw_html_dir, cleaned_html_dir)
    
    print("Chunking cleaned HTML files...")
    process_files(cleaned_html_dir, chunked_output_dir)
    
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
