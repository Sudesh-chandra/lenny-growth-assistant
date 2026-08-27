"""
Transcript ingestion script - loads Lenny's Podcast transcripts from the
ChatPRD/lennys-podcast-transcripts repository format.

Transcript format:
  - Each episode is in: data/transcripts/episodes/<guest-slug>/transcript.md
  - YAML frontmatter with: guest, title, youtube_url, publish_date, keywords, etc.
  - Body has speaker-labeled transcript with timestamps

Usage:
    cd backend
    python -m scripts.ingest
"""

import os
import sys
import re
import uuid
import glob
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.services.vector_store import get_vector_store

setup_logging()
logger = get_logger(__name__)


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from a markdown file.
    Returns (metadata_dict, body_text).
    """
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter_str = parts[1].strip()
    body = parts[2].strip()
    
    metadata = {}
    
    # Simple YAML parser for the frontmatter fields we need
    for line in frontmatter_str.split("\n"):
        line = line.strip()
        if not line or line.startswith("-"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            if value:
                metadata[key] = value
    
    # Parse keywords list
    keywords = []
    in_keywords = False
    for line in frontmatter_str.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("keywords:"):
            in_keywords = True
            continue
        if in_keywords:
            if line_stripped.startswith("- "):
                keywords.append(line_stripped[2:].strip())
            elif line_stripped and not line_stripped.startswith("-"):
                in_keywords = False
    
    if keywords:
        metadata["keywords"] = ", ".join(keywords)
    
    return metadata, body


def extract_guest_from_path(filepath: str) -> str:
    """Extract guest name slug from the file path."""
    # Path: .../transcripts/<guest-slug>/transcript.md
    parts = Path(filepath).parts
    for i, part in enumerate(parts):
        if part == "transcripts" and i + 1 < len(parts) and parts[i + 1] != "episodes":
            return parts[i + 1].replace("-", " ").title()
        if part == "episodes" and i + 1 < len(parts):
            return parts[i + 1].replace("-", " ").title()
    # Fallback: use parent directory name
    parent = Path(filepath).parent.name
    if parent and parent not in ("transcripts", "episodes", "data"):
        return parent.replace("-", " ").title()
    return "Unknown Guest"


def load_transcripts(transcript_dir: str) -> List[Dict[str, Any]]:
    """
    Load transcript files from the episodes directory structure.
    Each episode is in: <transcript_dir>/episodes/<guest-slug>/transcript.md
    """
    transcripts = []
    
    # Find all transcript.md files
    # Structure: <transcript_dir>/<guest-slug>/transcript.md
    pattern = os.path.join(transcript_dir, "*", "transcript.md")
    files = glob.glob(pattern)
    
    if not files:
        # Fallback: try episodes subdirectory
        pattern = os.path.join(transcript_dir, "episodes", "*", "transcript.md")
        files = glob.glob(pattern)
    
    if not files:
        # Fallback: try flat .txt files
        pattern = os.path.join(transcript_dir, "*.txt")
        files = glob.glob(pattern)
    
    logger.info("found_transcript_files", count=len(files))
    
    for filepath in sorted(files):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            if filepath.endswith(".md"):
                metadata, body = parse_frontmatter(content)
                
                # Extract guest from frontmatter or path
                guest = metadata.get("guest", extract_guest_from_path(filepath))
                title = metadata.get("title", guest)
                
                # Remove speaker labels and timestamps for cleaner chunks
                # Keep the text content only
                clean_body = clean_transcript_body(body)
                
                transcripts.append({
                    "content": clean_body,
                    "metadata": {
                        "episode": title,
                        "guest": guest,
                        "publish_date": metadata.get("publish_date", ""),
                        "youtube_url": metadata.get("youtube_url", ""),
                        "keywords": metadata.get("keywords", ""),
                        "source_file": os.path.relpath(filepath, transcript_dir),
                    },
                })
            else:
                # Plain text file
                filename = os.path.basename(filepath)
                episode_name = filename.replace(".txt", "").replace("_", " ").replace("-", " ")
                
                transcripts.append({
                    "content": content,
                    "metadata": {
                        "episode": episode_name.title(),
                        "guest": extract_guest_from_path(filepath),
                        "source_file": filename,
                    },
                })
            
        except Exception as e:
            logger.error("failed_to_load", file=filepath, error=str(e))
    
    return transcripts


def clean_transcript_body(body: str) -> str:
    """
    Clean transcript body by removing speaker labels and timestamps
    while preserving the actual conversation text.
    """
    lines = body.split("\n")
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # Skip the "## Transcript" header
        if stripped.startswith("## Transcript"):
            continue
        
        # Skip standalone timestamps like "(00:01:21):"
        if re.match(r'^\(\d{2}:\d{2}:\d{2}\):?$', stripped):
            continue
        
        # Remove speaker labels with timestamps: "Andy Johns (00:00:00):"
        # Keep the text after the timestamp
        speaker_match = re.match(r'^[A-Za-z][\w\s]+?\(\d{2}:\d{2}:\d{2}\):\s*', stripped)
        if speaker_match:
            text_after = stripped[speaker_match.end():]
            if text_after:
                cleaned_lines.append(text_after)
            continue
        
        # Remove standalone timestamps at start: "(00:01:21):"
        ts_match = re.match(r'^\(\d{2}:\d{2}:\d{2}\):\s*', stripped)
        if ts_match:
            text_after = stripped[ts_match.end():]
            if text_after:
                cleaned_lines.append(text_after)
            continue
        
        # Regular text line
        cleaned_lines.append(stripped)
    
    return " ".join(cleaned_lines)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    Tries to break at sentence boundaries.
    """
    if not text.strip():
        return []
    
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_length = len(sentence)
        
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # Keep overlap by retaining last few sentences
            overlap_sentences = []
            overlap_len = 0
            for s in reversed(current_chunk):
                if overlap_len + len(s) > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_len += len(s) + 1
            
            current_chunk = overlap_sentences
            current_length = overlap_len
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def ingest_transcripts():
    """Main ingestion function."""
    logger.info("starting_ingestion")
    
    # Find transcript directory
    transcript_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "transcripts"
    )
    
    if not os.path.exists(transcript_dir):
        logger.error("transcript_dir_not_found", path=transcript_dir)
        print(f"Transcript directory not found: {transcript_dir}")
        print("Please clone the transcripts repo into data/transcripts/")
        return
    
    # Load transcripts
    transcripts = load_transcripts(transcript_dir)
    if not transcripts:
        logger.warning("no_transcripts_found")
        print("No transcript files found.")
        return
    
    logger.info("transcripts_loaded", count=len(transcripts))
    print(f"\nLoaded {len(transcripts)} episodes")
    
    # Initialize vector store
    vector_store = get_vector_store()
    
    # Process each transcript and store incrementally
    total_chunks = 0
    total_episodes = len(transcripts)
    
    for i, transcript in enumerate(transcripts):
        content = transcript["content"]
        metadata = transcript["metadata"]
        
        # Chunk the text
        chunks = chunk_text(
            content,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        
        episode_ids = []
        episode_documents = []
        episode_metadatas = []
        
        for j, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            chunk_id = str(uuid.uuid4())
            episode_ids.append(chunk_id)
            episode_documents.append(chunk)
            episode_metadatas.append({
                **metadata,
                "chunk_index": j,
                "total_chunks": len(chunks),
            })
        
        # Store this episode's chunks immediately
        if episode_ids:
            vector_store.add_chunks(
                ids=episode_ids,
                documents=episode_documents,
                metadatas=episode_metadatas,
            )
            total_chunks += len(episode_ids)
        
        # Progress update every 10 episodes
        if (i + 1) % 10 == 0 or (i + 1) == total_episodes:
            store_count = vector_store.get_count()
            print(f"  [{i + 1}/{total_episodes}] Stored {total_chunks} chunks so far (vector store: {store_count})")
    
    # Final summary
    final_count = vector_store.get_count()
    if final_count > 0:
        logger.info("ingestion_complete",
                     total_chunks=final_count,
                     total_transcripts=len(transcripts))
        print(f"\nIngestion complete!")
        print(f"  Episodes processed: {len(transcripts)}")
        print(f"  Chunks in vector store: {final_count}")
    else:
        print("No chunks were stored. Check your transcript files.")


if __name__ == "__main__":
    ingest_transcripts()
