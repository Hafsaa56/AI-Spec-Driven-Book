import os
import re
from pathlib import Path
from typing import List, Dict, Any
import markdown
from bs4 import BeautifulSoup
import tiktoken

class DocumentChunk:
    def __init__(self, content: str, metadata: Dict[str, Any], chunk_id: str = None):
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id or self._generate_chunk_id()

    def _generate_chunk_id(self) -> str:
        import hashlib
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"chunk_{content_hash}"

def extract_markdown_headers(content: str) -> Dict[str, str]:
    """Extract headers from markdown content to preserve structure."""
    headers = {}
    lines = content.split('\n')

    for line in lines:
        # Match markdown headers like # Header, ## Header, etc.
        header_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2).strip()
            if level == 1:
                headers['title'] = header_text
            elif level == 2:
                headers['section'] = header_text

    return headers

def parse_markdown_file(file_path: Path) -> Dict[str, Any]:
    """Parse a markdown file and extract content with metadata."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract headers for metadata
    headers = extract_markdown_headers(content)

    # Convert markdown to plain text for embedding
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')
    plain_text = soup.get_text()

    metadata = {
        'source_file': str(file_path),
        'relative_path': str(file_path.relative_to(Path.cwd())),
        'title': headers.get('title', ''),
        'section': headers.get('section', ''),
        'file_size': len(content),
        'created_at': os.path.getctime(file_path),
        'updated_at': os.path.getmtime(file_path)
    }

    return {
        'content': plain_text,
        'metadata': metadata
    }

def chunk_text(text: str, max_words: int = 500) -> List[str]:
    """Split text into chunks of approximately max_words while preserving sentences."""
    sentences = re.split(r'[.!?]+\s+', text)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        if current_word_count + sentence_word_count <= max_words:
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
        else:
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')

            # If a single sentence is longer than max_words, split it by max_words
            if sentence_word_count > max_words:
                words = sentence.split()
                for i in range(0, len(words), max_words):
                    chunk_words = words[i:i + max_words]
                    chunks.append(' '.join(chunk_words))
                current_chunk = []
                current_word_count = 0
            else:
                current_chunk = [sentence]
                current_word_count = sentence_word_count

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return [chunk for chunk in chunks if chunk.strip()]

def scan_docs_directory(docs_path: str = "docs") -> List[Path]:
    """Scan the docs directory for all markdown files."""
    docs_dir = Path(docs_path)
    if not docs_dir.exists():
        print(f"Docs directory {docs_dir} does not exist. Creating it...")
        docs_dir.mkdir(parents=True, exist_ok=True)
        return []

    # Find all markdown files recursively, excluding common ignore patterns
    exclude_patterns = ['.git', '__pycache__', '.venv', 'venv', 'node_modules', '.DS_Store']
    markdown_files = []

    for file_path in docs_dir.rglob("*.md"):
        # Check if any part of the path matches exclude patterns
        if not any(exclude in str(file_path) for exclude in exclude_patterns):
            markdown_files.append(file_path)

    return markdown_files

def process_docs(docs_path: str = "docs") -> List[DocumentChunk]:
    """Process all markdown files in the docs directory and return chunks."""
    print(f"Scanning {docs_path} directory for markdown files...")
    markdown_files = scan_docs_directory(docs_path)

    print(f"Found {len(markdown_files)} markdown files to process")

    all_chunks = []
    for file_path in markdown_files:
        print(f"Processing: {file_path}")
        try:
            parsed_doc = parse_markdown_file(file_path)
            content = parsed_doc['content']
            metadata = parsed_doc['metadata']

            # Split content into chunks
            chunks = chunk_text(content, max_words=500)

            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)

                doc_chunk = DocumentChunk(
                    content=chunk,
                    metadata=chunk_metadata
                )
                all_chunks.append(doc_chunk)

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue

    print(f"Successfully processed {len(all_chunks)} chunks from {len(markdown_files)} files")
    return all_chunks

if __name__ == "__main__":
    # Process documents and print summary
    chunks = process_docs()
    print(f"\nIngestion complete! Processed {len(chunks)} document chunks")

    # Print sample of first chunk to verify
    if chunks:
        print(f"First chunk preview: {chunks[0].content[:100]}...")
        print(f"Metadata: {chunks[0].metadata}")