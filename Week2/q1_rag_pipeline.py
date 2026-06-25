"""
Question 1: Build a Minimal RAG Pipeline from Scratch
=====================================================
Agentic AI LS26 - Week 2 Assignment

Parts:
  A - Fixed-size chunking with overlap
  B - Embedding with all-MiniLM-L6-v2, manual cosine similarity, top-k retrieval
  C - Generation with google/flan-t5-base via HuggingFace
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------------------------------------------------------------------
# Global state (initialised by setup())
# ---------------------------------------------------------------------------
model = None            # SentenceTransformer embedding model
chunk_embeddings = None  # numpy array of shape (num_chunks, embedding_dim)
chunks = None           # list of chunk strings
gen_model = None        # HuggingFace flan-t5-base model
tokenizer = None        # Tokenizer for the generation model


# ========================== PART A: Chunking ===============================

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """
    Split `text` into chunks of ~chunk_size words,
    with `overlap` words shared between consecutive chunks.
    Returns a list of chunk strings.
    """
    words = text.split()
    result = []
    start = 0
    step = chunk_size - overlap

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        result.append(chunk)
        start += step

    return result


# ================== PART B: Embedding & Vector Store =======================

def cosine_similarity(a, b):
    """
    Compute cosine similarity between vectors a and b.
    Formula: cos(theta) = A.B / ||A|| ||B||
    (No sklearn used.)
    """
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


def retrieve(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    """Return the top_k most similar chunks to `query` with cosine scores."""
    query_embedding = model.encode(query)
    scores = [cosine_similarity(query_embedding, ce) for ce in chunk_embeddings]
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], float(scores[i])) for i in top_indices]


# ========================= PART C: Generation ==============================

def rag_answer(query: str) -> str:
    """Retrieve relevant chunks and generate an answer using the LLM."""
    results = retrieve(query, top_k=3)
    context = "\n\n".join(chunk for chunk, _ in results)
    prompt = f"""Answer the question using ONLY the context below.
If the answer is not in the context, say 'I don't know'.

Context:
{context}

Question: {query}
Answer:"""
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = gen_model.generate(**inputs, max_new_tokens=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# ============================ Setup ========================================

def setup(text: str):
    """Initialise the RAG pipeline: chunk the text, embed, and load the LLM."""
    global model, chunk_embeddings, chunks, gen_model, tokenizer

    # Chunk the document
    chunks = chunk_text(text)

    # Load embedding model and embed all chunks
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunk_embeddings = model.encode(chunks)
    print(f"  Embedded {len(chunks)} chunks -> shape {chunk_embeddings.shape}")

    # Load generation model
    print("Loading generation model (google/flan-t5-base)...")
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    gen_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    print("  Generator ready.\n")


# ============================ Main Demo ====================================

if __name__ == "__main__":
    # Load document
    with open("input_text.txt", "r", encoding="utf-8") as f:
        text = f.read()

    setup(text)

    # ---- Part A output ----
    print("=" * 60)
    print("PART A: Chunking")
    print("=" * 60)
    print(f"Total number of chunks: {len(chunks)}\n")

    # ---- Part B output: 3 queries ----
    print("=" * 60)
    print("PART B: Embedding & Retrieval  (3 queries)")
    print("=" * 60)

    queries_b = [
        "What are the elements of emotional intelligence?",
        "Can leadership be trained or is it innate?",
        "What is the role of feedback in leadership training?",
    ]

    for q in queries_b:
        print(f"\nQuery: {q}")
        print("-" * 55)
        results = retrieve(q, top_k=3)
        for rank, (chunk, score) in enumerate(results, 1):
            preview = " ".join(chunk.split()[:30]) + " ..."
            print(f"  Top-{rank} [cosine score = {score:.4f}]: {preview}")

    # ---- Part C output: 2 queries ----
    print("\n" + "=" * 60)
    print("PART C: Generation  (RAG answers)")
    print("=" * 60)

    # Answerable query
    q_in = "What are the five elements of emotional intelligence?"
    print(f"\nQuery (answerable): {q_in}")
    answer_in = rag_answer(q_in)
    print(f"Answer: {answer_in}")

    # Out-of-scope query (hallucination guard)
    q_out = "What is the chemical formula for photosynthesis?"
    print(f"\nQuery (out-of-scope): {q_out}")
    answer_out = rag_answer(q_out)
    print(f"Answer: {answer_out}")

    print("\nDone!")
