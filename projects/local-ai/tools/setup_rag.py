#!/usr/bin/env python3.11
"""
Setup script for configuring a local RAG (Retrieval Augmented Generation) system.
This tool helps set up a simple RAG system using local embeddings and models.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from common import setup_env  # Import the common setup_env function

def check_requirements():
    """Check if required packages are installed."""
    required = ['chromadb', 'sentence-transformers', 'torch', 'pypdf', 'python-dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env_rag():
    """Setup environment for RAG."""
    env_string = """# RAG Settings
OLLAMA_API_URL=http://localhost:11434/v1
EMBEDDINGS_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./data/vectordb
DOCUMENTS_PATH=./data/documents
LOCAL_MODEL_NAME=codellama
CHUNK_SIZE=500
CHUNK_OVERLAP=50
"""
    setup_env(env_string)  # Call the common setup_env function

def setup_rag():
    """Setup the RAG system files."""
    # Create necessary directories
    for dir_path in ["data/documents", "data/vectordb"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create the main RAG implementation
    with open("rag_system.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import os
from pathlib import Path
from typing import List, Dict
import chromadb
from sentence_transformers import SentenceTransformer
import torch
import requests
from dotenv import load_dotenv
import pypdf

load_dotenv()

class LocalRAG:
    def __init__(self):
        self.embeddings_model = SentenceTransformer(os.getenv("EMBEDDINGS_MODEL"))
        self.chroma_client = chromadb.PersistentClient(path=os.getenv("VECTOR_DB_PATH"))
        self.collection = self.chroma_client.get_or_create_collection("documents")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))
        
    def process_document(self, file_path: str):
        """Process and index a document."""
        print(f"Processing {file_path}...")
        
        # Read document
        text = ""
        if file_path.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                pdf = pypdf.PdfReader(f)
                for page in pdf.pages:
                    text += page.extract_text()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Split into chunks
        chunks = self._split_text(text)
        
        # Generate embeddings and store
        embeddings = self.embeddings_model.encode(chunks)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            ids=[f"{Path(file_path).stem}_{i}" for i in range(len(chunks))]
        )
        
    def query(self, question: str, k: int = 3) -> str:
        """Query the RAG system."""
        # Get question embedding
        question_embedding = self.embeddings_model.encode(question)
        
        # Retrieve relevant chunks
        results = self.collection.query(
            query_embeddings=[question_embedding.tolist()],
            n_results=k
        )
        
        # Construct prompt with context
        context = "\\n\\n".join(results['documents'][0])
        prompt = f"Based on the following context, please answer the question.\\n\\nContext:\\n{context}\\n\\nQuestion: {question}"
        
        # Query local model
        response = requests.post(
            f"{os.getenv('OLLAMA_API_URL')}/chat/completions",
            json={
                "model": os.getenv("LOCAL_MODEL_NAME"),
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )
        
        return response.json()['choices'][0]['message']['content']
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
        return chunks

def main():
    parser = argparse.ArgumentParser(description="Setup local RAG system")
    parser.add_argument("--model", default="codellama", help="Local model to use (default: codellama)")
    args = parser.parse_args()
    
    print("Setting up local RAG system...")
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_env_rag()
    
    # Setup RAG system
    setup_rag()
    
    print(f"""
Setup complete! To use the RAG system:

1. Start your local model:
   ollama run {args.model}

2. Place your documents (PDFs or text files) in the data/documents directory

3. Run the RAG system:
   python rag_system.py

The system will:
- Process and index your documents using local embeddings
- Store vectors in a local ChromaDB database
- Use your local model for generating answers
- Keep all data and processing local

Example usage:
1. Add some PDF documents to data/documents/
2. Run the system and ask questions about your documents
3. The system will retrieve relevant context and generate answers locally
""")

if __name__ == "__main__":
    main() 