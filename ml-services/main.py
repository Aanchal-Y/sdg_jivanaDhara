from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI(title="SDG ML Service", version="1.0")

# --- Models / Pipelines ---
# Small, fast zero-shot classifier
zero_shot = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-1",  # fast, decent for intents
)

# Tiny text-gen for demo; swap to your HF Inference endpoint if needed
generator = pipeline("text-generation", model="sshleifer/tiny-gpt2")

# Embedding model
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --- Mock knowledge base per SDG (could be replaced by Pinecone/Milvus) ---
SDG_LABELS = {
    "sdg2": "Zero Hunger",
    "sdg3": "Good Health and Well-Being",
    "sdg4": "Quality Education",
    "sdg6": "Clean Water and Sanitation",
    "sdg7": "Affordable and Clean Energy",
    "sdg11": "Sustainable Cities and Communities"
}

KB = [
    {"id": "p1", "sdg": "sdg2", "title": "Community Grain Banks", "desc": "Village-level grain storage & fair distribution"},
    {"id": "p2", "sdg": "sdg3", "title": "Mobile Health Vans", "desc": "Basic diagnostics & telemedicine"},
    {"id": "p3", "sdg": "sdg4", "title": "Tablet Classrooms", "desc": "Offline-first curriculum with teacher aid"},
    {"id": "p4", "sdg": "sdg6", "title": "Solar Water Purifiers", "desc": "Low-cost UV + membrane"},
    {"id": "p5", "sdg": "sdg7", "title": "Community Solar Microgrid", "desc": "Prepaid smart meters"},
    {"id": "p6", "sdg": "sdg11", "title": "Waste Segregation & Compost", "desc": "Ward-level MRF & civic incentives"}
]
KB_TEXTS = [f"{k['sdg']} | {k['title']} | {k['desc']}" for k in KB]
KB_EMB = embedder.encode(KB_TEXTS, normalize_embeddings=True)

# --- Schemas ---
class RecommendRequest(BaseModel):
    query: str
    sdg: Optional[str] = None  # "sdg2", ...
    top_k: int = 3

class RecommendItem(BaseModel):
    id: str
    title: str
    description: str
    score: float
    resources: List[str]
    timeline: str
    confidence: float

class AnalyzeRequest(BaseModel):
    text: str

class StoreProofRequest(BaseModel):
    record: Dict[str, Any]

# --- Helpers ---
def search_kb(query: str, sdg: Optional[str], k: int = 3):
    q = embedder.encode([query], normalize_embeddings=True)[0]
    scores = np.array(KB_EMB @ q)  # cosine (because normalized)
    # Filter by SDG if provided
    if sdg:
        mask = np.array([1 if item["sdg"] == sdg else 0 for item in KB])
        scores = scores * mask
    top_idx = scores.argsort()[::-1][:k]
    results = []
    for i in top_idx:
        item = KB[i]
        results.append({
            "id": item["id"],
            "title": item["title"],
            "description": item["desc"],
            "score": float(scores[i])
        })
    return results

# --- Routes ---
@app.get("/")
def root():
    return {"ok": True, "service": "sdg-ml", "labels": SDG_LABELS}

@app.post("/recommendations", response_model=List[RecommendItem])
def recommendations(req: RecommendRequest):
    # 1) Intent / SDG guess
    labels = list(SDG_LABELS.values())
    z = zero_shot(req.query, candidate_labels=labels, multi_label=True)
    label_scores = dict(zip(z["labels"], z["scores"]))
    guessed_sdg = req.sdg
    if not guessed_sdg:
        # map best label back to key
        best_label = z["labels"][0]
        for k, v in SDG_LABELS.items():
            if v == best_label:
                guessed_sdg = k
                break

    # 2) Retrieve relevant items
    hits = search_kb(req.query, guessed_sdg, req.top_k)

    # 3) Generate short tailored suggestion (demo)
    suggestions = []
    for h in hits:
        gen = generator(
            f"Suggest next steps for '{h['title']}' in context: {req.query}\nPlan:",
            max_length=60,
            num_return_sequences=1,
            do_sample=False,
        )[0]["generated_text"]
        suggestions.append(
            RecommendItem(
                id=h["id"],
                title=h["title"],
                description=gen.split("Plan:", 1)[-1].strip(),
                score=round(h["score"], 4),
                resources=["Local Partners", "Community Org", "Mobile App"],
                timeline="2-4 months",
                confidence=min(0.99, max(0.5, h["score"] + label_scores.get(SDG_LABELS.get(guessed_sdg, ""), 0))),
            )
        )

    return suggestions

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    # trivial analysis stub
    z = zero_shot(req.text, candidate_labels=["high impact", "medium impact", "low impact"], multi_label=False)
    return {
        "label": z["labels"][0],
        "score": z["scores"][0],
        "insights": [
            "Community engagement appears feasible.",
            "Consider low-cost pilots before scaling.",
            "Collect baseline metrics (reach, cost/benefit)."
        ]
    }
