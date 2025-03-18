import os
import re
from bs4 import BeautifulSoup


def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    keep_tags = ['a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']

    for tag in reversed(soup.find_all()):
        if tag.name not in keep_tags:
            tag.replace_with_children() if hasattr(tag, 'contents') else tag.extract()

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        a_tag.attrs = {}  # Remove all attributes
        if href:
            a_tag['href'] = href

    for tag in soup.find_all():
        if tag.name != 'a':
            tag.attrs = {}

    cleaned_html = re.sub(r'\s+', ' ', str(soup))
    return re.sub(r'>\s+<', '><', cleaned_html)


def process_cleaning(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            with open(input_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            cleaned_html = clean_html(html_content)

            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_html)

            print(f"Cleaned {filename} successfully!")
