import requests
from bs4 import BeautifulSoup
import re

def fetch_alice_text():
    url = "https://www.gutenberg.org/cache/epub/28885/pg28885.txt"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch text: HTTP {response.status_code}")
        return []
    
    # Save the raw text file
    with open('alice_chapters.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("Downloaded Alice in Wonderland text and saved to alice_chapters.txt")
    
    # Process the text to identify chapters
    content = response.text
    lines = content.split('\n')
    chapter_pattern = re.compile(r'CHAPTER ([IVXLCDM]+)\.', re.IGNORECASE)
    
    chapters = []
    current_chapter = {"title": "", "content": []}
    in_chapter = False
    
    for line in lines:
        line = line.strip()
        
        # Look for chapter headers
        chapter_match = chapter_pattern.search(line)
        if chapter_match:
            # Save previous chapter if it exists
            if current_chapter["title"] and current_chapter["content"]:
                chapters.append(current_chapter)
            
            # Start new chapter
            current_chapter = {"title": line, "content": []}
            in_chapter = True
        elif in_chapter:
            current_chapter["content"].append(line)
    
    # Add the last chapter
    if current_chapter["title"] and current_chapter["content"]:
        chapters.append(current_chapter)
    
    return chapters

def save_chapters(chapters):
    # This function is now redundant since we save the raw text directly
    # But we'll keep it for compatibility with existing code
    print(f"Processed {len(chapters)} chapters from Alice in Wonderland")

if __name__ == "__main__":
    alice_chapters = fetch_alice_text()
    print(f"Extracted {len(alice_chapters)} chapters")
    
    save_chapters(alice_chapters)
