# UniQbot: AI-Driven Chatbot for Northeastern OGS

## Project Description
UniQbot is an AI-powered chatbot designed to enhance document Q&A capabilities for Northeastern University's Office of Global Services (OGS). The system leverages Retrieval-Augmented Generation (RAG) to provide instant, reliable answers to student queries, reducing dependency on office hours and improving overall accessibility to OGS services.

This repository contains the implementation of two different language models (GPT-2 and DistilGPT-2) for comparison as part of our approach to creating an effective Q&A system.

## Project Goals
- Provide 24/7 access to OGS information through an AI chatbot
- Enhance student experience by offering immediate answers to common queries
- Compare different language models to optimize response quality
- Create a scalable solution that can be integrated with platforms like Slack/Discord/Teams

## Dataset Details
- **Source**: Northeastern University's Office of Global Services (OGS) website
- **Collection Method**: Web scraping via custom NortheasternScraper class
- **Format**: HTML files with extracted web content
- **Content**: Information about international student services, visa requirements, and OGS policies
- **Preprocessing**: HTML files are parsed to extract clean text for model input

## Project Components
Under Work
### 1. Web Scraper
The project includes a custom web scraper (`scraper.py`) specifically designed for collecting data from the Northeastern OGS website. Features include:
- Respectful crawling with delays and proper headers
- Multi-threaded scraping for efficiency
- Automatic filtering of non-HTML content
- Domain-restricted crawling
- Organized file saving structure

### 2. Model Comparison
This iteration implements and compares two different transformer-based language models:
1. **GPT-2** - OpenAI's full GPT-2 model
2. **DistilGPT-2** - A distilled version of GPT-2 that is smaller and faster

The implementation allows for direct comparison of response quality and generation speed between these models.

## Clone the Repository

```bash
git clone https://github.com/namansnghl/UniQbot-rag.git
cd UniQbot-rag
```

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Data Collection (Optional)
If you need to collect fresh data from the OGS website:
```bash
python scraper.py
```
This will populate the `scraped_pages` directory with HTML files.

### Step 2: Model Comparison
Run the model comparison script on the collected data:
```bash
python model_comparison.py
```

### Step 3: Custom Queries
For custom queries, modify the `question` variable in the `model_comparison.py` script.

## Project Structure

```
UniQbot-rag/
├── model_comparison.py       # Main script for comparing GPT-2 and DistilGPT-2
├── scraper.py                # Web scraper for OGS website
├── requirements.txt          # Dependencies
├── scraped_pages/            # Directory for scraped HTML files
├── README.md                 # This file
└── docs/                     # Additional documentation
```

## Ethical Considerations
This scraper is designed for educational purposes only. Please be respectful of Northeastern University's website resources:
- The scraper includes deliberate delays to minimize server load
- It adheres to robots.txt guidelines implicitly through domain restrictions
- This implementation is specifically for the DS 5500 course project

## Future Development
- Implement RAG architecture using vector databases (ChromaDB/Neo4J)
- Develop API endpoints using FastAPI
- Create web dashboard for user interaction
- Add Slack/Discord/Teams integration
- Deploy on AWS infrastructure

## Team Members
- Shreyashri Vishwanath Athani
- Naman Singhal
- Sudarshan Paranjape

## Course Information
DS 5500 | Capstone Project | Northeastern University
