const express = require('express');
const path = require('path');
const fs = require('fs');
const { JSDOM } = require('jsdom');
const { OpenAI } = require('openai'); // You can also use Llama or another local model
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable JSON parsing and CORS
app.use(express.json());
app.use(cors());

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Initialize OpenAI or your local model
// const openai = new OpenAI({
//   apiKey: process.env.OPENAI_API_KEY, // Add your API key as an environment variable
// });

// In-memory storage for the indexed content (in production, use a vector database)
let websiteContent = [];

// Function to scrape and index HTML content
function scrapeAndIndexWebsite() {
  const pages = [
    { path: 'public/index.html', url: '/' },
    { path: 'public/faqs.html', url: '/faqs' },
    { path: 'public/f1-students.html', url: '/f1-students' },
    { path: 'public/contact.html', url: '/contact' }
  ];

  websiteContent = [];

  pages.forEach(page => {
    try {
      const htmlContent = fs.readFileSync(page.path, 'utf8');
      const dom = new JSDOM(htmlContent);
      const document = dom.window.document;
      
      // Extract text content from main sections
      const mainContent = document.querySelector('main');
      if (mainContent) {
        // Extract headers
        const headers = Array.from(mainContent.querySelectorAll('h1, h2, h3')).map(h => h.textContent.trim());
        
        // Extract paragraphs
        const paragraphs = Array.from(mainContent.querySelectorAll('p')).map(p => p.textContent.trim());
        
        // Extract list items
        const listItems = Array.from(mainContent.querySelectorAll('li')).map(li => li.textContent.trim());
        
        // Combine all content with its URL
        websiteContent.push({
          url: page.url,
          title: document.title,
          headers: headers,
          content: [...headers, ...paragraphs, ...listItems].join(' ')
        });
      }
    } catch (error) {
      console.error(`Error processing ${page.path}:`, error);
    }
  });

  console.log(`Indexed ${websiteContent.length} pages.`);
}

// RAG endpoint
app.post('/api/rag', async (req, res) => {
  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    // Simple retrieval - in production use semantic search or embeddings
    // Find relevant content from website
    const relevantContent = websiteContent
      .filter(page => {
        const lowerContent = page.content.toLowerCase();
        const lowerQuery = query.toLowerCase();
        
        // Check if any words from the query appear in the content
        const queryWords = lowerQuery.split(' ').filter(word => word.length > 3);
        return queryWords.some(word => lowerContent.includes(word));
      })
      .map(page => `Page: ${page.title}\nContent: ${page.content.slice(0, 500)}...`)
      .join('\n\n');

    // Default context if no relevant content found
    let context = "This is a website about F1 student visas, with pages for FAQs, student resources, and contact information.";
    
    if (relevantContent) {
      context = relevantContent;
    }

    // In a production environment, call an LLM API like this:
    // const response = await openai.chat.completions.create({
    //   model: "gpt-3.5-turbo", // or your local model
    //   messages: [
    //     {
    //       role: "system",
    //       content: `You are a helpful assistant for a website. Answer questions based on the following content:\n${context}`
    //     },
    //     {
    //       role: "user",
    //       content: query
    //     }
    //   ],
    //   temperature: 0.7,
    // });
    // const answer = response.choices[0].message.content;

    // For this example, simulate a response
    let answer = "I'm sorry, I don't have specific information about that on this website.";
    
    // Simple keyword matching for demo
    const lowerQuery = query.toLowerCase();
    if (lowerQuery.includes('f1') || lowerQuery.includes('student') || lowerQuery.includes('visa')) {
      answer = "F1 visas are for international students. Be sure to maintain full-time enrollment, get authorization before working, and keep your I-20 valid. Check out our F1-Students page for more details!";
    } else if (lowerQuery.includes('contact') || lowerQuery.includes('reach') || lowerQuery.includes('email')) {
      answer = "You can contact us by email at info@ragchatbotdemo.com, by phone at +1 (555) 123-4567, or by filling out the form on our Contact page.";
    } else if (lowerQuery.includes('rag') || lowerQuery.includes('chatbot') || lowerQuery.includes('how do you work')) {
      answer = "I'm a RAG (Retrieval-Augmented Generation) chatbot. I search through the content of this website to find relevant information to answer your questions. This helps me provide accurate information specific to this site's content.";
    }

    res.json({ answer });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'An error occurred while processing your request.' });
  }
});

// Catch-all route to serve the main index.html for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Index the website before starting the server
scrapeAndIndexWebsite();

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});