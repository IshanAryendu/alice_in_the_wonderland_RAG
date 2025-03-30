import os
from langchain_ollama import OllamaEmbeddings  # Updated import
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import re

def load_alice_text():
    with open("alice_chapters.txt", "r") as f:
        content = f.read()
    
    # Look for the table of contents to identify chapter titles
    toc_pattern = re.compile(r'CONTENTS\s+(.+?)LIST OF THE PLATES', re.DOTALL)
    toc_match = toc_pattern.search(content)
    
    chapters = []
    
    if toc_match:
        # Extract chapter info from table of contents
        toc_content = toc_match.group(1)
        chapter_entries = re.findall(r'([IVX]+)\.\s+(.*?)\s+(\d+)', toc_content)
        
        # Now find each chapter in the text
        for num, title, page in chapter_entries:
            chapter_header = f"CHAPTER {num}"
            chapter_pattern = re.compile(f"{chapter_header}.*?(?=CHAPTER [IVX]+|End of Project Gutenberg)", re.DOTALL)
            chapter_match = chapter_pattern.search(content)
            
            if chapter_match:
                chapter_content = chapter_match.group(0)
                chapters.append({
                    "title": f"CHAPTER {num}. {title.strip()}",
                    "content": chapter_content.strip()
                })
    
    # If we couldn't extract chapters from TOC, try direct search
    if not chapters:
        print("Using direct chapter search method...")
        # Look for chapter headers with the format [Sidenote: _Chapter Title_]
        chapter_pattern = re.compile(r'\[Sidenote: _(.*?)_\](.*?)(?=\[Sidenote: _|End of Project Gutenberg|\Z)', re.DOTALL)
        matches = chapter_pattern.findall(content)
        
        for i, (title, content) in enumerate(matches):
            if "chapter" in title.lower() or "down the rabbit" in title.lower():
                chapters.append({
                    "title": title.strip(),
                    "content": content.strip()
                })
    
    # If still no chapters, try another approach
    if not chapters:
        print("Using content-based extraction...")
        # Extract the main story content (between start and end markers)
        start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK ALICE'S ADVENTURES IN WONDERLAND ***"
        end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK ALICE'S ADVENTURES IN WONDERLAND ***"
        
        if start_marker in content and end_marker in content:
            main_content = content.split(start_marker)[1].split(end_marker)[0].strip()
            
            # Split by chapter markers if possible
            chapter_splits = re.split(r'CHAPTER [IVXLCDM]+\.', main_content)
            if len(chapter_splits) > 1:
                for i, chapter_content in enumerate(chapter_splits[1:], 1):  # Skip the first split (before first chapter)
                    chapters.append({
                        "title": f"CHAPTER {i}",
                        "content": chapter_content.strip()
                    })
            else:
                # If no chapter splits, just use the whole content as one document
                chapters.append({
                    "title": "Alice's Adventures in Wonderland",
                    "content": main_content
                })
    
    print(f"Extracted {len(chapters)} chapters")
    return chapters

def debug_alice_file():
    """Debug function to check the content of alice_chapters.txt"""
    try:
        with open("alice_chapters.txt", "r") as f:
            content = f.read()
        
        print(f"File size: {len(content)} bytes")
        print(f"First 200 characters: {content[:200]}")
        
        # Check for various markers
        print("Checking for key markers:")
        markers = [
            "CHAPTER I", 
            "CHAPTER II", 
            "DOWN THE RABBIT-HOLE",
            "[Sidenote:",
            "CONTENTS",
            "*** START OF THE PROJECT GUTENBERG EBOOK"
        ]
        
        for marker in markers:
            print(f"  '{marker}': {'Found' if marker in content else 'Not found'}")
        
        # Extract a sample around a potential chapter
        if "[Sidenote:" in content:
            idx = content.find("[Sidenote:")
            print(f"\nSample around [Sidenote: (±100 chars):\n{content[max(0, idx-100):idx+100]}")
        
        return True
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

def create_rag():
    # Debug the alice_chapters.txt file
    if not debug_alice_file():
        print("Problem with alice_chapters.txt file. Please check if it exists and has content.")
        return None
        
    # Load the text
    chapters = load_alice_text()
    
    if not chapters:
        print("No chapters extracted. Please check the format of alice_chapters.txt")
        return None
    
    # Create documents with metadata
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    for chapter in chapters:
        chunks = text_splitter.split_text(chapter["content"])
        for i, chunk in enumerate(chunks):
            # Create Document objects with page_content and metadata
            from langchain.schema import Document
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "chapter": chapter["title"],
                        "stanza": f"Stanza {i+1}"  # Approximating stanzas as chunks
                    }
                )
            )
    
    print(f"Created {len(documents)} document chunks")
    
    # Initialize Ollama embeddings with a model that supports embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
    
    # Ensure Ollama is running and model is available
    try:
        # Test the embeddings with a simple text
        print("Testing embedding model...")
        test_embedding = embeddings.embed_query("test")
        print(f"Embedding dimension: {len(test_embedding)}")
        if not test_embedding or len(test_embedding) == 0:
            raise ValueError("Embedding model returned empty embeddings")
    except Exception as e:
        print(f"Error testing embeddings: {e}")
        print("Please ensure Ollama is running and the nomic-embed-text model is installed.")
        print("Run: ollama pull nomic-embed-text")
        return None
    
    # Create vector store
    print("Creating vector store...")
    try:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="./alice_chroma_db"
        )
        print("Vector store created successfully")
        return vectorstore
    except Exception as e:
        print(f"Error creating vector store: {e}")
        print("Try using a different embedding model or check if Ollama is running correctly")
        return None

def query_rag(query, vectorstore):
    # Initialize Ollama LLM
    llm = Ollama(model="gemma3:1b")
    
    # Create retrieval QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    
    # Query the system
    result = qa_chain({"query": query})
    
    return {
        "answer": result["result"],
        "sources": [
            {
                "content": doc.page_content,
                "chapter": doc.metadata["chapter"],
                "stanza": doc.metadata["stanza"]
            }
            for doc in result["source_documents"]
        ]
    }

if __name__ == "__main__":
    # Create or load the RAG system
    if not os.path.exists("./alice_chroma_db"):
        print("Creating RAG system...")
        vectorstore = create_rag()
    else:
        print("Loading existing RAG system...")
        embeddings = OllamaEmbeddings(model="gemma3:1b")
        vectorstore = Chroma(persist_directory="./alice_chroma_db", embedding_function=embeddings)
    
    # Interactive query loop
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
