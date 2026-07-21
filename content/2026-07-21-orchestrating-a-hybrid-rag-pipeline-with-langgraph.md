Title: Orchestrating a Hybrid RAG Pipeline with LangGraph
Date: 2026-07-21
Category: GenAI
Tags: GenAI, AI, RAG, LangGraph, LangChain, Vector-Search, BM25, Reranking
Slug: orchestrating-a-hybrid-rag-pipeline-with-langgraph

A Hybrid RAG pipeline that combines BM25, dense retrieval, Reciprocal Rank Fusion (RRF), and a cross-encoder reranker isn't really one step — it's a chain of decisions. Each stage takes an input, transforms it, and hands it off. That's exactly the pattern LangGraph is built for: modeling a workflow as a graph of nodes (functions) connected by edges (control flow), with a shared state object that flows through the whole thing.

Instead of a linear Python script that calls functions one after another, LangGraph turns the pipeline into an explicit, inspectable graph. This matters once the pipeline grows — for example, when you want to add query rewriting, conditional reranking, or a fallback path when retrieval confidence is low.

## Recap: The Existing Pipeline

The current architecture, in plain terms:

1. **Query comes in**
2. **BM25 retrieval** — sparse, keyword-based search over the corpus
3. **Dense retrieval** — embedding-based semantic search (vector store)
4. **RRF (Reciprocal Rank Fusion)** — merges the two ranked lists into one, using the formula `score = sum(1 / (k + rank))` across both result sets
5. **Cross-encoder reranking** — takes the fused top-N candidates and reranks them with a more expensive, more accurate model that scores (query, document) pairs jointly
6. **Final context** passed to the LLM for answer generation

Each of these is a natural LangGraph node.

## Why LangGraph Fits This Project

A plain function chain works fine for a linear pipeline. LangGraph earns its keep the moment you need conditional routing, parallel execution, retries, or a fallback path. For Hybrid RAG, all of those scenarios are realistic — and wiring them into a graph from the start means adding them later is a matter of new nodes and edges, not rewritten logic.

## Step 1: Define Shared State

LangGraph passes a state object between nodes. For this pipeline, the state carries the query and the intermediate results at each stage:

```python
from typing import TypedDict, List

class RAGState(TypedDict):
    query: str
    bm25_results: List[dict]
    dense_results: List[dict]
    fused_results: List[dict]
    reranked_results: List[dict]
    answer: str
```

## Step 2: Define Each Stage as a Node

```python
from langgraph.graph import StateGraph, END

def bm25_node(state: RAGState) -> RAGState:
    results = bm25_search(state["query"], top_k=20)
    return {"bm25_results": results}

def dense_node(state: RAGState) -> RAGState:
    results = dense_search(state["query"], top_k=20)
    return {"dense_results": results}

def rrf_fusion_node(state: RAGState) -> RAGState:
    fused = reciprocal_rank_fusion(
        state["bm25_results"],
        state["dense_results"],
        k=60
    )
    return {"fused_results": fused[:20]}

def rerank_node(state: RAGState) -> RAGState:
    reranked = cross_encoder_rerank(
        state["query"],
        state["fused_results"],
        top_k=5
    )
    return {"reranked_results": reranked}

def generate_node(state: RAGState) -> RAGState:
    context = format_context(state["reranked_results"])
    answer = llm_generate(state["query"], context)
    return {"answer": answer}
```

## Step 3: Wire the Graph

BM25 and dense retrieval don't depend on each other, so they can run as parallel branches that both feed into fusion:

```python
graph = StateGraph(RAGState)

graph.add_node("bm25", bm25_node)
graph.add_node("dense", dense_node)
graph.add_node("fuse", rrf_fusion_node)
graph.add_node("rerank", rerank_node)
graph.add_node("generate", generate_node)

graph.set_entry_point("bm25")
graph.add_edge("bm25", "dense")
graph.add_edge("dense", "fuse")
graph.add_edge("fuse", "rerank")
graph.add_edge("rerank", "generate")
graph.add_edge("generate", END)

app = graph.compile()
```

For genuinely parallel execution, LangGraph supports fan-out from a single entry node into both `bm25` and `dense`, then a join at `fuse` — the graph waits for both branches before continuing.

## Step 4: Run It

```python
result = app.invoke({"query": "What is reciprocal rank fusion?"})
print(result["answer"])
```

## What This Buys You Over a Plain Function Chain

**Conditional routing** — Add an edge that checks `fused_results` confidence and skips reranking entirely if the top result already has a high fusion score, saving the cross-encoder's compute cost on easy queries:

```python
def should_rerank(state: RAGState) -> str:
    top_score = state["fused_results"][0]["score"] if state["fused_results"] else 0
    return "rerank" if top_score < 0.8 else "generate"

graph.add_conditional_edges("fuse", should_rerank, {
    "rerank": "rerank",
    "generate": "generate"
})
```

**Retry and fallback logic** — If dense retrieval returns nothing (empty vector store, embedding API failure), route to a fallback node that leans entirely on BM25 instead of failing the whole pipeline.

**Observability** — Because state flows explicitly node-to-node, you can log or inspect `state` after any stage — useful for debugging why a particular document got surfaced or dropped during fusion or reranking.

**Composability for future features** — Query rewriting, multi-hop retrieval, or a self-correction loop all become new nodes and edges rather than rewritten pipeline logic.

**Checkpointing** — LangGraph supports persisting state at each node, which means a long-running query can resume from the last completed step rather than restarting from scratch.

## The Golden Rule of Building RAG Pipelines

**A well-structured pipeline produces more reliable answers than a powerful model alone.**

Even the best LLM cannot compensate for poor retrieval. Getting BM25, dense search, fusion, and reranking right — and keeping the stages cleanly separated — is what makes the difference between a RAG system that works in demos and one that works in production.

## Trade-offs to Keep in Mind

**Added complexity for a linear pipeline.** If the pipeline never branches or needs retries, a plain function chain is simpler to read and debug. LangGraph earns its keep once conditional logic, parallelism, or loops enter the picture.

**Learning curve.** State typing, node signatures, and graph compilation add a layer that a beginner-level project might not need right away.

**Latency isn't automatically improved.** LangGraph doesn't make BM25 or the cross-encoder faster — the win is in structure and control flow, not raw speed. Actual parallel speedup only happens if you configure genuine fan-out execution.

## Final Thought

LangGraph turns a Hybrid RAG pipeline from a linear script into an explicit, controllable graph. The structure pays for itself the moment you need to add conditional reranking, handle retrieval failures gracefully, or extend the pipeline with new stages. Start small — wrap the existing functions as nodes, add the conditional-rerank-skip logic first, and the rest of the graph patterns follow naturally from there.
