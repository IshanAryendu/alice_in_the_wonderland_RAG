# Alice in Wonderland RAG System

A Retrieval-Augmented Generation (RAG) system that allows you to query information from Lewis Carroll's "Alice in Wonderland" using the Gemma 3 language model.

## Features

- Fetches and processes the full text of "Alice in Wonderland" from Project Gutenberg
- Builds a vector database with chapter and stanza metadata
- Uses Ollama's nomic-embed-text model for embeddings and Gemma 3 for text generation
- Provides source references with chapter and stanza information
- Interactive query mode and command-line options

## Prerequisites

- Python 3.10+
- Ollama installed locally (https://ollama.com)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/alice-rag.git
   cd alice-rag
   ```

2. Install the required packages:
   ```
   pip install requests beautifulsoup4 langchain langchain_community langchain_ollama chromadb ollama
   ```

3. Pull the required models using Ollama:
   ```
   ollama pull gemma3:1b
   ollama pull nomic-embed-text
   ```

4. Make sure Ollama is running:
   ```
   ollama serve
   ```

## Usage

### Interactive Mode

Simply run the main script without arguments to enter interactive mode:

```
python main.py
```

This will:
1. Fetch the Alice in Wonderland text if not already downloaded
2. Build the RAG system if not already built
3. Start an interactive query session

### Command-line Options

The script supports the following command-line arguments:

- `--fetch`: Fetch and process the Alice in Wonderland text
- `--build-rag`: Build the RAG system
- `--query "your question"`: Query the RAG system with a specific question

Examples:

```
# Fetch the text
python main.py --fetch

# Build the RAG system
python main.py --build-rag

# Query the system
python main.py --query "What happened at the Mad Hatter's tea party?"
```

## Troubleshooting

- **Empty Embeddings Error**: Make sure Ollama is running with `ollama serve` and that you've pulled the required models with `ollama pull gemma3:1b` and `ollama pull nomic-embed-text`.
- **Model Not Found**: If you get a model not found error, try using a different Ollama model by changing the model name in `alice_rag.py`.

## Project Structure

- `main.py`: Main entry point with CLI interface
- `fetch_alice.py`: Fetches and processes the text from Project Gutenberg
- `alice_rag.py`: Implements the RAG system using LangChain and Ollama

## License

This project is licensed under the MIT License - see the LICENSE file for details.
