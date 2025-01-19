## API Proxy Setup

The repository includes a tool to help you set up a proxy that routes AI API calls through local models to check content for secrets. This is particularly useful when you want to ensure no sensitive information is accidentally sent to external API providers.

### Setup Instructions

1. Navigate to the tools directory:
```bash
cd tools
```

2. Run the setup script:
```bash
python setup_proxy.py
```

The script will:
- Install required dependencies
- Create a `.env` file with default settings
- Set up a proxy server that intercepts API calls

### Configuration

The default configuration uses:
- Port 8080 for the proxy server
- Port 11434 for the local model (Ollama)
- CodeLlama as the default model for content checking

You can customize these settings by:
- Editing the `.env` file
- Using command line arguments:
```bash
python setup_proxy.py --port 9000 --model mistral
```

### How It Works

1. The proxy intercepts OpenAI API calls
2. Before forwarding the request, it uses your local model to check for sensitive content
3. If sensitive information is detected, the request is blocked
4. Otherwise, the request is forwarded to your local model

This provides an extra layer of security when using AI APIs while keeping your data private. 

## Local RAG System

The repository includes a tool to set up a local RAG (Retrieval Augmented Generation) system. This allows you to query your documents using AI while keeping all processing and data local.

### Setup Instructions

1. Navigate to the tools directory:
```bash
cd tools
```

2. Run the setup script:
```bash
python setup_rag.py
```

The script will:
- Install required dependencies (ChromaDB, SentenceTransformers, etc.)
- Create necessary directories for documents and vector storage
- Set up a RAG system with local embeddings and model integration

### Usage

1. Place your documents (PDFs or text files) in the `data/documents` directory
2. Start your local model (e.g., `ollama run codellama`)
3. Run the RAG system: `python rag_system.py`
4. Ask questions about your documents

The system uses:
- Local embeddings (SentenceTransformers)
- Local vector storage (ChromaDB)
- Local LLM for answer generation
- Completely offline operation

## Other Potential Tools

Here are some other tools we could add to enhance local AI development:

1. **Fine-tuning Setup**
   - Tool to prepare datasets
   - Configure and run fine-tuning on local models
   - Evaluate model performance

2. **Model Quantization**
   - Convert models to different quantization levels
   - Benchmark performance vs. memory usage
   - Easy switching between quantized versions

3. **Prompt Engineering Lab**
   - Test prompts with different models
   - Compare responses and performance
   - Save and version control prompts

4. **Model Evaluation Suite**
   - Run standardized tests
   - Compare different models
   - Generate performance reports

5. **Dataset Creation Tools**
   - Convert various data formats
   - Clean and preprocess data
   - Create training/validation splits

6. **Model API Gateway**
   - Load balance between models
   - Fallback handling
   - Response caching

7. **Cost & Performance Monitoring**
   - Track token usage
   - Monitor response times
   - Compare model efficiency

8. **Local Knowledge Base**
   - Web scraping to local storage
   - Automatic document processing
   - Structured data extraction

Each of these tools would help developers work more effectively with local AI models while maintaining data privacy and control. 