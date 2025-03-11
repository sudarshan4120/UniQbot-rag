import os
from bs4 import BeautifulSoup
import re

def clean_html(html_content):
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Only keeping tags that have info
    keep_tags = ['a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']
    
    # Find all tags
    all_tags = soup.find_all()
    
    # Iterate through tags in reverse to avoid incomplete parsing
    for tag in reversed(all_tags):
        # If tag is not in our keep list
        if tag.name not in keep_tags:
            # If it has content, replace the tag with its contents
            if hasattr(tag, 'contents'):
                tag.replace_with_children()
            else:
                tag.extract()
    
    # For <a> tags, make sure to only keep href attribute
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        # Remove all attributes
        a_tag.attrs = {}
        # Add back only href if it existed
        if href:
            a_tag['href'] = href
    
    # For all remaining tags, remove all attributes except href for <a>
    for tag in soup.find_all():
        if tag.name != 'a':
            tag.attrs = {}
    
    # Get the cleaned HTML
    cleaned_html = str(soup)
    
    # Optional: remove extra whitespace and empty lines
    cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
    cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)
    
    return cleaned_html

if __name__ == "__main__":
    # Directory containing HTML files
    input_dir = 'streamlit/data/scraped_pages'
    output_dir = 'data/cleaned_html'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each file in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)  # Keep the same filename
            
            # Read HTML file
            with open(input_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Clean the HTML
            cleaned_html = clean_html(html_content)
            
            # Save the cleaned HTML
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_html)
            
            print(f"Cleaned {filename} successfully!")
    
