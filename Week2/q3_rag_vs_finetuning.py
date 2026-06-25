"""
Question 3: RAG vs Fine-Tuning: Decision and Demo
===================================================
Agentic AI LS26 - Week 2 Assignment

Part A: Decision tree for RAG vs Fine-Tuning.
Part B: Hallucination stress test with bar chart.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend (works without display)
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Import RAG pipeline components from Q1
from q1_rag_pipeline import setup, retrieve, rag_answer


# ===================== PART A: Decision Tree ==============================

def recommend_approach(scenario: dict) -> str:
    """
    Input keys:
      - data_changes_frequently: bool
      - need_specific_output_format: bool
      - budget: str  # 'low' | 'medium' | 'high'
      - latency_sensitive: bool
      - knowledge_type: str  # 'factual' | 'behavioral' | 'both'
    Returns one of: 'RAG', 'Fine-Tuning', 'RAG + Fine-Tuning',
    'Prompt Engineering only' with a 1-sentence justification.
    """
    data_changes = scenario["data_changes_frequently"]
    format_need  = scenario["need_specific_output_format"]
    budget       = scenario["budget"]
    latency      = scenario["latency_sensitive"]
    knowledge    = scenario["knowledge_type"]

    # ---- Both factual + behavioural needs => combine ----
    if knowledge == "both":
        if budget == "low":
            return ("RAG + Fine-Tuning",
                    "Both factual retrieval and behavioural adaptation are needed; "
                    "even on a tight budget the combination is essential for quality.")
        return ("RAG + Fine-Tuning",
                "Combining RAG for dynamic factual knowledge with Fine-Tuning "
                "for specialised output behaviour yields the best results.")

    # ---- Factual knowledge ----
    if knowledge == "factual":
        if data_changes:
            return ("RAG",
                    "Frequently changing factual data is best served by RAG's "
                    "dynamic retrieval without costly retraining.")
        if budget == "low" and not format_need and not latency:
            return ("Prompt Engineering only",
                    "Static factual needs with a low budget and no special "
                    "format requirements can be addressed through careful prompt design.")
        return ("RAG",
                "Factual knowledge retrieval is RAG's core strength, providing "
                "grounded answers from a document store.")

    # ---- Behavioural knowledge ----
    if knowledge == "behavioral":
        if format_need and budget != "low":
            return ("Fine-Tuning",
                    "Specific output formats and behavioural patterns require "
                    "fine-tuning the model on curated examples.")
        if budget == "low" and not format_need:
            return ("Prompt Engineering only",
                    "Simple behavioural adjustments on a low budget are best "
                    "handled through well-crafted prompt engineering.")
        return ("Fine-Tuning",
                "Behavioural adaptation - tone, style, and format - is best "
                "achieved through fine-tuning on representative data.")

    # Fallback
    return ("Prompt Engineering only",
            "The requirements are simple enough to be addressed with "
            "prompt engineering alone.")


# ================ PART B: Hallucination Stress Test =======================

def stress_test():
    """Run 6 queries (3 answerable + 3 out-of-scope), log results, and plot."""

    # 3 answerable queries (answers exist in the leadership document)
    answerable = [
        "What are the five elements of emotional intelligence?",
        "Which company started a Training Facility at an affiliate college?",
        "What did Plato believe about training a good leader?",
    ]

    # 3 out-of-scope queries (plausible-sounding but factually absent)
    out_of_scope = [
        "What is the chemical formula for photosynthesis?",
        "Which programming language is best for machine learning?",
        "What are the main causes of climate change?",
    ]

    all_queries = answerable + out_of_scope
    labels = ["Answerable"] * len(answerable) + ["Out-of-scope"] * len(out_of_scope)
    colors = ["green"] * len(answerable) + ["red"] * len(out_of_scope)

    print("\n" + "=" * 70)
    print("PART B: Hallucination Stress Test")
    print("=" * 70)

    scores = []
    for i, query in enumerate(all_queries):
        results = retrieve(query, top_k=3)
        top_chunk, top_score = results[0]
        answer = rag_answer(query)

        # First 100 words of top chunk
        top_chunk_preview = " ".join(top_chunk.split()[:100])

        print(f"\n{'~' * 70}")
        print(f"Query {i+1} [{labels[i]}]: {query}")
        print(f"Top chunk (first 100 words): {top_chunk_preview}")
        print(f"Cosine similarity score:     {top_score:.4f}")
        print(f"LLM answer:                  {answer}")

        scores.append(top_score)

    # ---- Bar chart ----
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(all_queries))
    bars = ax.bar(x, scores, color=colors, edgecolor="black", linewidth=0.8)

    # Add score labels on bars
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{score:.3f}", ha="center", va="bottom", fontsize=9)

    short_labels = [f"Q{i+1}: " + (q[:35] + "..." if len(q) > 35 else q)
                    for i, q in enumerate(all_queries)]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Cosine Similarity Score")
    ax.set_title("Hallucination Stress Test: Cosine Scores by Query Type")
    ax.set_ylim(0, max(scores) + 0.15)

    legend_elements = [
        Patch(facecolor="green", edgecolor="black", label="Answerable"),
        Patch(facecolor="red",   edgecolor="black", label="Out-of-scope"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()
    plt.savefig("hallucination_stress_test.png", dpi=150)
    print(f"\nBar chart saved to 'hallucination_stress_test.png'")

    # ---- Analysis ----
    avg_answerable = np.mean(scores[:len(answerable)])
    avg_oos = np.mean(scores[len(answerable):])
    print(f"\n{'=' * 70}")
    print("ANALYSIS")
    print(f"{'=' * 70}")
    print(f"Average cosine score (answerable):   {avg_answerable:.4f}")
    print(f"Average cosine score (out-of-scope): {avg_oos:.4f}")

    if avg_answerable > avg_oos:
        print(
            "\nAs expected, answerable queries have HIGHER similarity scores,\n"
            "confirming the retriever surfaces relevant chunks for in-scope queries.\n"
            "Lower scores for out-of-scope queries help the grounding prompt\n"
            "produce 'I don't know' answers, acting as a hallucination guard."
        )
    else:
        print(
            "\nUnexpected: out-of-scope scores are similar to or higher than\n"
            "answerable scores. This may indicate the grounding prompt needs\n"
            "strengthening or the document has incidental overlap with\n"
            "out-of-scope topics. If the pipeline hallucinated on an out-of-scope\n"
            "query (gave a confident wrong answer), the cosine score may be\n"
            "suspiciously high due to superficial lexical overlap, or the grounding\n"
            "prompt may be too weak to enforce 'I don't know' responses."
        )


# ============================ Main =========================================

if __name__ == "__main__":
    # ---- Part A: Decision Tree ----
    print("=" * 70)
    print("PART A: Decision Tree  -  recommend_approach()")
    print("=" * 70)

    scenarios = [
        {
            "name": "Customer-support chatbot with frequently changing FAQs",
            "data_changes_frequently": True,
            "need_specific_output_format": False,
            "budget": "medium",
            "latency_sensitive": True,
            "knowledge_type": "factual",
        },
        {
            "name": "Medical report generator with strict format",
            "data_changes_frequently": False,
            "need_specific_output_format": True,
            "budget": "high",
            "latency_sensitive": False,
            "knowledge_type": "behavioral",
        },
        {
            "name": "Legal research assistant needing citations + specific format",
            "data_changes_frequently": True,
            "need_specific_output_format": True,
            "budget": "high",
            "latency_sensitive": False,
            "knowledge_type": "both",
        },
        {
            "name": "Simple internal Q&A on static company policy (low budget)",
            "data_changes_frequently": False,
            "need_specific_output_format": False,
            "budget": "low",
            "latency_sensitive": False,
            "knowledge_type": "factual",
        },
        {
            "name": "News summarisation service with daily updates",
            "data_changes_frequently": True,
            "need_specific_output_format": False,
            "budget": "medium",
            "latency_sensitive": True,
            "knowledge_type": "factual",
        },
    ]

    for sc in scenarios:
        name = sc["name"]
        recommendation, justification = recommend_approach(sc)
        print(f"\nScenario: {name}")
        print(f"  -> {recommendation}")
        print(f"     {justification}")

    # ---- Part B: Hallucination Stress Test ----
    print("\n\nLoading RAG pipeline from Q1...")
    with open("input_text.txt", "r", encoding="utf-8") as f:
        text = f.read()
    setup(text)

    stress_test()

    print("\nDone!")
