"""POI Semantic Search API - Deploy Ready (FastAPI)"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
import time
import os

from poi_semantic_filter import (
    filter_with_scores as semantic_search,
    filter_pois_by_token_keyword as semantic_filter,
)

try:
    from poi_embedding_filter import filter_pois_by_tfidf, filter_pois_by_token_keyword_old
    HAS_TFIDF = True
except Exception:
    HAS_TFIDF = False
    filter_pois_by_tfidf = None
    filter_pois_by_token_keyword_old = None

app = FastAPI(title="POI Semantic Search API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

POIS: List[Dict[str, Any]] = [
    {"pid": 1, "location": "Noida", "sheet": "H32", "pincode": "201003",
     "landmark": "", "food": "Burger", "restaurant": "ABC Restaurant",
     "zone": "ABC", "phone": "12345", "food_type": "veg"},
    {"pid": 2, "location": "Delhi", "sheet": "H42", "pincode": "110001",
     "landmark": "Near XYZ Mall", "food": "Pizza", "restaurant": "XYZ Restaurant",
     "zone": "XYZ", "phone": "67890", "food_type": "non-veg"},
    {"pid": 3, "location": "Noida", "sheet": "H43", "pincode": "201301",
     "landmark": "Near City Mall", "food": "Burger", "restaurant": "Burger House",
     "zone": "ABC", "phone": "55555", "food_type": "veg"},
    {"pid": 4, "location": "Delhi", "sheet": "D12", "pincode": "110045",
     "landmark": "Opposite Metro Gate 3", "food": "Chicken Biryani",
     "restaurant": "Dum Mast Biryani", "zone": "South", "phone": "98110", "food_type": "non-veg"},
    {"pid": 5, "location": "Noida", "sheet": "N21", "pincode": "201301",
     "landmark": "Sector 18 Market", "food": "Paneer Tikka",
     "restaurant": "Shuddh Veg Dhaba", "zone": "ABC", "phone": "98220", "food_type": "veg"},
    {"pid": 6, "location": "Gurgaon", "sheet": "G07", "pincode": "122001",
     "landmark": "Cyber Hub", "food": "Sushi",
     "restaurant": "Tokyo Table", "zone": "Cyber", "phone": "98330", "food_type": "non-veg"},
    {"pid": 7, "location": "Delhi", "sheet": "D33", "pincode": "110017",
     "landmark": "Near IIT Gate", "food": "Masala Dosa",
     "restaurant": "Madras Cafe", "zone": "South", "phone": "98440", "food_type": "veg"},
    {"pid": 8, "location": "Noida", "sheet": "H55", "pincode": "201303",
     "landmark": "Near Amity University", "food": "Egg Roll",
     "restaurant": "Kolkata Rolls", "zone": "Express", "phone": "98550", "food_type": "non-veg"},
    {"pid": 9, "location": "Delhi", "sheet": "D51", "pincode": "110006",
     "landmark": "Chandni Chowk", "food": "Chole Bhature",
     "restaurant": "Old Delhi Foods", "zone": "Old Delhi", "phone": "98660", "food_type": "veg"},
    {"pid": 10, "location": "Noida", "sheet": "H60", "pincode": "201304",
     "landmark": "Gaur City Mall", "food": "Veg Pizza",
     "restaurant": "Italiano Veg", "zone": "West", "phone": "98770", "food_type": "veg"},
    {"pid": 11, "location": "Delhi", "sheet": "D77", "pincode": "110092",
     "landmark": "Near Akshardham", "food": "Mutton Keema",
     "restaurant": "Zaika Non-Veg", "zone": "East", "phone": "98880", "food_type": "non-veg"},
    {"pid": 12, "location": "Gurgaon", "sheet": "G21", "pincode": "122018",
     "landmark": "Sohna Road", "food": "Veg Burger",
     "restaurant": "Green Burger Co.", "zone": "South City", "phone": "98990", "food_type": "veg"},
]
class SearchRequest(BaseModel):
    query: str = Field(..., description="e.g. not vegetarian")
    method: str = Field("semantic", description="semantic|keyword|tfidf")
    threshold: float = 0.05
    top_k: Optional[int] = 5

class AddPoiRequest(BaseModel):
    location: str = ""
    sheet: str = ""
    pincode: str = ""
    landmark: str = ""
    food: str = ""
    restaurant: str = ""
    zone: str = ""
    phone: str = ""
    food_type: str = "veg"

def do_search(query: str, method: str, threshold: float, top_k):
    q = (query or "").strip()
    if not q:
        return [], 0
    tokens = [q]
    t0 = time.time()
    m = (method or "semantic").lower()
    if m == "keyword":
        if filter_pois_by_token_keyword_old is None:
            out = []
            for p in POIS:
                blob = " ".join(str(v).lower() for v in p.values())
                if q.lower() in blob:
                    out.append((p, 1.0))
            res = out[:top_k] if top_k else out
        else:
            matched = filter_pois_by_token_keyword_old(POIS, tokens)
            res = [(p, 1.0) for p in matched]
            res = res[:top_k] if top_k else res
    elif m == "tfidf":
        if not HAS_TFIDF:
            raise HTTPException(status_code=400, detail="sklearn missing")
        res = filter_pois_by_tfidf(POIS, tokens, threshold=threshold, top_k=top_k)
    else:
        res = semantic_search(POIS, tokens, threshold=threshold, top_k=top_k)
    ms = round((time.time() - t0) * 1000, 1)
    fmt = [{"poi": p, "score": round(float(s), 4)} for p, s in res]
    return fmt, ms

@app.get("/api/health")
def health():
    return {"status": "ok", "total_pois": len(POIS), "tfidf": HAS_TFIDF}

@app.get("/api/pois")
def list_pois():
    return {"count": len(POIS), "pois": POIS}

@app.post("/api/search")
def search_post(b: SearchRequest):
    r, ms = do_search(b.query, b.method, b.threshold, b.top_k)
    return {"query": b.query, "method": b.method, "count": len(r), "time_ms": ms, "results": r}

@app.get("/api/search")
def search_get(q: str = "", method: str = "semantic", threshold: float = 0.05, top_k: int = 5):
    r, ms = do_search(q, method, threshold, top_k if top_k > 0 else None)
    return {"query": q, "method": method, "count": len(r), "time_ms": ms, "results": r}

@app.post("/api/pois")
def add_poi(b: AddPoiRequest):
    pid = max([p["pid"] for p in POIS], default=0) + 1
    poi = {"pid": pid, **b.dict()}
    POIS.append(poi)
    return {"message": "added", "poi": poi}

@app.delete("/api/pois/{pid}")
def del_poi(pid: int):
    global POIS
    n = len(POIS)
    POIS = [p for p in POIS if p["pid"] != pid]
    if len(POIS) == n:
        raise HTTPException(status_code=404, detail="not found")
    return {"message": "deleted", "count": len(POIS)}

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def home():
    idx = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return {"msg": "API ok: /docs"}

