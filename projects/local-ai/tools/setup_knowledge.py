#!/usr/bin/env python3.11
"""
Setup script for local knowledge base.
This tool helps set up a system for collecting, processing, and querying local knowledge.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

def check_requirements():
    """Check if required packages are installed."""
    required = ['beautifulsoup4', 'requests', 'trafilatura', 'chromadb', 'sentence-transformers', 'python-dotenv', 'fastapi', 'uvicorn']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env():
    """Setup environment configuration."""
    env_path = Path(".env")

    if not env_path.exists():
        print("Creating .env file...")
        with open(env_path, "w") as f:
            f.write("""# Knowledge Base Settings
KB_PORT=8000
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./data/knowledge
SOURCES_PATH=./data/sources
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=50
SCRAPE_DEPTH=2
MAX_URLS_PER_DOMAIN=10
""")
        print("Created .env file with default settings")
    else:
        print(".env file already exists")

def setup_knowledge_base():
    """Setup the knowledge base system files."""
    # Create necessary directories
    for dir_path in ["data/knowledge", "data/sources", "scripts"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Create web scraper
    with open("scripts/scraper.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
import json
import os
from pathlib import Path
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
import requests
import trafilatura
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class WebScraper:
    def __init__(self):
        self.sources_path = Path(os.getenv("SOURCES_PATH"))
        self.max_depth = int(os.getenv("SCRAPE_DEPTH"))
        self.max_urls = int(os.getenv("MAX_URLS_PER_DOMAIN"))
        self.visited: Set[str] = set()
    
    def scrape_url(self, url: str, depth: int = 0) -> Dict:
        \"\"\"Scrape content and links from URL.\"\"\"
        if depth > self.max_depth or url in self.visited:
            return {}
        
        self.visited.add(url)
        print(f"Scraping: {url}")
        
        try:
            # Download and extract content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return {}
            
            content = trafilatura.extract(downloaded)
            if not content:
                return {}
            
            # Extract links for further scraping
            links = []
            if depth < self.max_depth:
                soup = BeautifulSoup(downloaded, 'html.parser')
                domain = urlparse(url).netloc
                domain_count = sum(1 for u in self.visited if domain in u)
                
                if domain_count < self.max_urls:
                    for a in soup.find_all('a', href=True):
                        link = urljoin(url, a['href'])
                        if (
                            urlparse(link).netloc == domain
                            and link not in self.visited
                        ):
                            links.append(link)
            
            return {
                "url": url,
                "content": content,
                "links": links
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {}
    
    def scrape_recursively(self, start_url: str) -> List[Dict]:
        \"\"\"Recursively scrape from starting URL.\"\"\"
        results = []
        urls_to_scrape = [start_url]
        
        while urls_to_scrape:
            url = urls_to_scrape.pop(0)
            result = self.scrape_url(url, depth=len(results))
            
            if result:
                results.append(result)
                urls_to_scrape.extend(result["links"])
        
        return results
    
    def save_results(self, results: List[Dict], domain: str):
        \"\"\"Save scraping results.\"\"\"
        output_file = self.sources_path / f"{domain}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved {len(results)} pages to {output_file}")

def main():
    scraper = WebScraper()
    
    # Example usage
    start_url = input("Enter URL to scrape: ")
    domain = urlparse(start_url).netloc.replace(".", "_")
    
    results = scraper.scrape_recursively(start_url)
    scraper.save_results(results, domain)

if __name__ == "__main__":
    main()
""")

    # Create knowledge base processor
    with open("scripts/process_knowledge.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
import json
import os
from pathlib import Path
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class KnowledgeProcessor:
    def __init__(self):
        self.sources_path = Path(os.getenv("SOURCES_PATH"))
        self.chunk_size = int(os.getenv("MAX_CHUNK_SIZE"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP"))
        self.embeddings_model = SentenceTransformer(os.getenv("EMBEDDINGS_MODEL"))
        self.db = chromadb.PersistentClient(path=os.getenv("VECTOR_DB_PATH"))
        self.collection = self.db.get_or_create_collection("knowledge")
    
    def process_sources(self):
        \"\"\"Process all source files.\"\"\"
        for file_path in self.sources_path.glob("*.json"):
            print(f"Processing {file_path}...")
            with open(file_path) as f:
                sources = json.load(f)
            
            for source in sources:
                chunks = self._chunk_text(source["content"])
                embeddings = self.embeddings_model.encode(chunks)
                
                # Store in vector database
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=chunks,
                    metadatas=[{"url": source["url"]}] * len(chunks),
                    ids=[f"{file_path.stem}_{i}" for i in range(len(chunks))]
                )
    
    def _chunk_text(self, text: str) -> List[str]:
        \"\"\"Split text into overlapping chunks.\"\"\"
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
        return chunks

def main():
    processor = KnowledgeProcessor()
    processor.process_sources()

if __name__ == "__main__":
    main()
""")

    # Create knowledge base API
    with open("scripts/knowledge_api.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Knowledge Base API")

# Initialize components
embeddings_model = SentenceTransformer(os.getenv("EMBEDDINGS_MODEL"))
db = chromadb.PersistentClient(path=os.getenv("VECTOR_DB_PATH"))
collection = db.get_or_create_collection("knowledge")

class Query(BaseModel):
    text: str
    num_results: int = 3

class SearchResult(BaseModel):
    text: str
    url: str
    score: float

@app.post("/search", response_model=List[SearchResult])
async def search_knowledge(query: Query):
    \"\"\"Search knowledge base.\"\"\"
    # Generate query embedding
    query_embedding = embeddings_model.encode(query.text)
    
    # Search vector database
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=query.num_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    search_results = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        search_results.append(SearchResult(
            text=doc,
            url=meta["url"],
            score=1.0 - (dist / 2.0)  # Convert distance to similarity score
        ))
    
    return search_results

@app.get("/stats")
async def get_stats():
    \"\"\"Get knowledge base statistics.\"\"\"
    return {
        "total_documents": collection.count(),
        "sources": len(set(m["url"] for m in collection.get()["metadatas"]))
    }

def main():
    import uvicorn
    port = int(os.getenv("KB_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
""")

def main():
    parser = argparse.ArgumentParser(description="Setup local knowledge base")
    args = parser.parse_args()

    print("Setting up local knowledge base...")

    # Check and install requirements
    check_requirements()

    # Setup environment
    setup_env()

    # Setup knowledge base
    setup_knowledge_base()

    print("""
Setup complete! To build and use your knowledge base:

1. Collect data:
   python scripts/scraper.py
   - Enter URLs to scrape
   - Data saved to data/sources/

2. Process knowledge:
   python scripts/process_knowledge.py
   - Chunks and embeds content
   - Stores in vector database

3. Start the API:
   python scripts/knowledge_api.py
   - Provides search endpoint
   - Serves on http://localhost:8000

The system provides:
- Web scraping with depth control
- Content extraction and cleaning
- Vector storage with ChromaDB
- Fast semantic search
- REST API access

Features:
- Recursive web scraping
- Content chunking
- Semantic embeddings
- Vector search
- URL tracking
- API access

API Endpoints:
- POST /search - Search knowledge base
- GET /stats - Get database statistics

Tips:
- Adjust scraping depth in .env
- Configure chunk sizes
- Monitor database growth
- Use API for integration
- Regular updates recommended
""")

if __name__ == "__main__":
    main()
