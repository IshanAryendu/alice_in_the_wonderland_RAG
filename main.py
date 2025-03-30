import os
import argparse
from fetch_alice import fetch_alice_text
from alice_rag import create_rag, query_rag
from langchain_ollama import OllamaEmbeddings  # Updated import
from langchain_community.vectorstores import Chroma

def main():
    parser = argparse.ArgumentParser(description="Alice in Wonderland RAG System")
    parser.add_argument("--fetch", action="store_true", help="Fetch and process Alice text")
    parser.add_argument("--build-rag", action="store_true", help="Build the RAG system")
    parser.add_argument("--query", type=str, help="Query the RAG system")
    
    args = parser.parse_args()
    
    if args.fetch:
        print("Fetching Alice in Wonderland text...")
        alice_chapters = fetch_alice_text()
        print(f"Extracted {len(alice_chapters)} chapters")
    
    if args.build_rag:
        print("Building RAG system...")
        vectorstore = create_rag()
        if vectorstore:
            print("RAG system built and saved to ./alice_chroma_db")
        else:
            print("Failed to build RAG system. See error messages above.")
    
    if args.query:
        if not os.path.exists("./alice_chroma_db"):
            print("Error: RAG system not built. Run --build-rag first.")
            return
            
        print(f"Querying: {args.query}")
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = Chroma(persist_directory="./alice_chroma_db", embedding_function=embeddings)
        result = query_rag(args.query, vectorstore)
        
        print("\nAnswer:", result["answer"])
        print("\nSources:")
        for i, source in enumerate(result["sources"]):
            print(f"\nSource {i+1}:")
            print(f"Chapter: {source['chapter']}")
            print(f"Stanza: {source['stanza']}")
            print(f"Excerpt: {source['content'][:150]}...")
    
    if not any([args.fetch, args.build_rag, args.query]):
        print("Interactive mode:")
        if not os.path.exists("alice_chapters.txt"):
            print("Fetching Alice in Wonderland text...")
            fetch_alice_text()
        
        if not os.path.exists("./alice_chroma_db"):
            print("Building RAG system...")
            vectorstore = create_rag()
            if not vectorstore:
                print("Failed to build RAG system. Exiting.")
                return
        
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
        vectorstore = Chroma(persist_directory="./alice_chroma_db", embedding_function=embeddings)
        
        while True:
            query = input("\nEnter your question about Alice in Wonderland (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break
                
            result = query_rag(query, vectorstore)
            
            print("\nAnswer:", result["answer"])
            print("\nSources:")
            for i, source in enumerate(result["sources"]):
                print(f"\nSource {i+1}:")
                print(f"Chapter: {source['chapter']}")
                print(f"Stanza: {source['stanza']}")
                print(f"Excerpt: {source['content'][:150]}...")

if __name__ == "__main__":
    main()
