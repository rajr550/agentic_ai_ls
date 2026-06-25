"""
Question 2: Chunking Strategy Showdown
=======================================
Agentic AI LS26 - Week 2 Assignment

Compares three chunking strategies and measures their effect on retrieval quality.
"""

import re
import numpy as np
from sentence_transformers import SentenceTransformer


# ====================== PART A: Three Chunkers ============================

def fixed_chunk(text: str, size: int = 300, overlap: int = 50) -> list[str]:
    """Fixed-size word-level chunking with overlap."""
    words = text.split()
    chunks = []
    start = 0
    step = size - overlap
    while start < len(words):
        chunk = " ".join(words[start : start + size])
        chunks.append(chunk)
        start += step
    return chunks


def sentence_chunk(text: str) -> list[str]:
    """
    Split at sentence boundaries ('. ', '? ', '! ').
    Group sentences into chunks of ~5 sentences each with 1-sentence overlap.
    """
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.?!])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    group_size = 5
    overlap = 1
    start = 0
    while start < len(sentences):
        end = min(start + group_size, len(sentences))
        chunk = " ".join(sentences[start:end])
        chunks.append(chunk)
        if end >= len(sentences):
            break
        start += group_size - overlap
    return chunks


def sliding_window_chunk(text: str, window: int = 400, step: int = 100) -> list[str]:
    """Each chunk is `window` words, starting every `step` words (heavy overlap)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + window, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start += step
    return chunks


# ====================== Utility ==========================================

def cosine_similarity(a, b):
    """Manual cosine similarity: cos(theta) = A.B / ||A|| ||B||  (no sklearn)."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


# ====================== PART B: Retrieval Comparison ======================

def build_retriever(chunks, model):
    """Embed chunks and return the embedding matrix."""
    embeddings = model.encode(chunks)
    return embeddings


def retrieve_top_k(query, chunks, embeddings, model, top_k=3):
    """Return top-k (chunk, score) tuples for a query."""
    q_emb = model.encode(query)
    scores = [cosine_similarity(q_emb, e) for e in embeddings]
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], float(scores[i])) for i in top_idx]


# ============================ Main =========================================

if __name__ == "__main__":
    # Load document
    with open("input_text.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # ---- Part A: chunk statistics ----
    strategies = {
        "Fixed-size":     fixed_chunk(text),
        "Sentence-based": sentence_chunk(text),
        "Sliding window":  sliding_window_chunk(text),
    }

    print("=" * 70)
    print("PART A: Chunking Strategy Statistics")
    print("=" * 70)
    header = f"{'Strategy':<20} | {'Chunks':>6} | {'Mean Len (wds)':>14} | {'Min Len':>7} | {'Max Len':>7}"
    print(header)
    print("-" * 70)

    for name, chnks in strategies.items():
        lengths = [len(c.split()) for c in chnks]
        print(
            f"{name:<20} | {len(chnks):>6} | {np.mean(lengths):>14.1f} | "
            f"{min(lengths):>7} | {max(lengths):>7}"
        )

    # ---- Part B: Retrieval comparison ----
    print("\n" + "=" * 70)
    print("PART B: Retrieval Comparison")
    print("=" * 70)

    # 5 manually written question-answer pairs from the document
    qa_pairs = [
        (
            "What are the five elements of emotional intelligence?",
            "self-awareness, self-regulation, motivation, empathy, and social skills",
        ),
        (
            "Who advanced the concept of emotional intelligence in leadership?",
            "Daniel Goleman",
        ),
        (
            "Which company started a Training Facility at an affiliate college?",
            "Bentley Motors",
        ),
        (
            "How much is spent on training managers every year in the United Kingdom?",
            "50 billion dollars",
        ),
        (
            "What leadership styles did Kurt Lewin identify?",
            "autocratic, democratic, and Laissez-faire",
        ),
    ]

    print("\nLoading embedding model (all-MiniLM-L6-v2)...")
    emb_model = SentenceTransformer("all-MiniLM-L6-v2")

    results_table = {}
    for name, chnks in strategies.items():
        print(f"  Embedding chunks for '{name}' strategy...")
        embeddings = build_retriever(chnks, emb_model)
        hits = 0
        for question, answer in qa_pairs:
            top3 = retrieve_top_k(question, chnks, embeddings, emb_model, top_k=3)
            # Check if the answer string appears in any of the top-3 chunks
            found = any(answer.lower() in chunk.lower() for chunk, _ in top3)
            if found:
                hits += 1
        results_table[name] = hits

    print(f"\n{'Strategy':<20} | {'Chunks':>6} | {'Mean Len':>10} | {'Hit Rate':>10}")
    print("-" * 60)
    for name, chnks in strategies.items():
        lengths = [len(c.split()) for c in chnks]
        hr = results_table[name]
        print(
            f"{name:<20} | {len(chnks):>6} | "
            f"{np.mean(lengths):>7.0f} wds | "
            f"    {hr}/5"
        )

    print("\nDone!")
