"""
POI Filtering using Embeddings (Semantic Search)
Install: pip install sentence-transformers scikit-learn numpy
Run: python poi_embedding_filter.py
"""
from typing import List, Dict, Tuple

poi_list = [
    {"pid": 1, "location": "Noida", "sheet": "H32", "pincode": "201003",
     "landmark": "", "food": "Burger", "restaurant": "ABC Restaurant",
     "zone": "ABC", "phone": "12345", "food_type": "veg"},
    {"pid": 2, "location": "Delhi", "sheet": "H42", "pincode": "110001",
     "landmark": "Near XYZ Mall", "food": "Pizza", "restaurant": "XYZ Restaurant",
     "zone": "XYZ", "phone": "67890", "food_type": "non-veg"},
    {"pid": 3, "location": "Noida", "sheet": "H43", "pincode": "201301",
     "landmark": "Near City Mall", "food": "Burger", "restaurant": "Burger House",
     "zone": "ABC", "phone": "55555", "food_type": "veg"}
]

token_keyword = ["non-veg"]


def poi_to_text(poi: Dict, exclude_fields=("pid", "phone", "sheet", "pincode")) -> str:
    parts = []
    for k, v in poi.items():
        if k in exclude_fields:
            continue
        if v is None or str(v).strip() == "":
            continue
        if k in ("food", "food_type", "restaurant"):
            parts.append(f"{k}: {v} {v}")
        else:
            parts.append(f"{k}: {v}")
    return ". ".join(parts)


def query_to_text(token_keyword: List[str]) -> str:
    return " ".join([str(t).strip() for t in token_keyword if str(t).strip() != ""])


def filter_pois_by_token_keyword_old(poi_list, token_keyword):
    filtered = []
    for poi in poi_list:
        for kw in token_keyword:
            kw = str(kw).lower().strip()
            for v in poi.values():
                if kw in str(v).lower():
                    filtered.append(poi)
                    break
            if poi in filtered:
                break
    return filtered


def filter_pois_by_tfidf(poi_list, token_keyword, threshold=0.10, top_k=None):
    if not poi_list or not token_keyword:
        return []
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    poi_texts = [poi_to_text(p) for p in poi_list]
    query_text = query_to_text(token_keyword)
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    poi_vecs = vec.fit_transform(poi_texts)
    q_vec = vec.transform([query_text])
    sims = cosine_similarity(poi_vecs, q_vec).flatten()
    res = [(p, float(s)) for p, s in zip(poi_list, sims) if float(s) >= threshold]
    res.sort(key=lambda x: x[1], reverse=True)
    return res[:top_k] if top_k else res


def filter_pois_by_embedding(poi_list, token_keyword,
                             model_name="all-MiniLM-L6-v2",
                             threshold=0.30, top_k=None):
    if not poi_list or not token_keyword:
        return []
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    print(f"[Embedding] Loading model: {model_name} ...")
    model = SentenceTransformer(model_name)
    poi_texts = [poi_to_text(p) for p in poi_list]
    query_text = query_to_text(token_keyword)
    print(f"[Embedding] Query: '{query_text}'")
    poi_emb = model.encode(poi_texts, normalize_embeddings=True,
                           show_progress_bar=False)
    q_emb = model.encode([query_text], normalize_embeddings=True,
                         show_progress_bar=False)
    sims = cosine_similarity(poi_emb, q_emb).flatten()
    res = [(p, float(s)) for p, s in zip(poi_list, sims) if float(s) >= threshold]
    res.sort(key=lambda x: x[1], reverse=True)
    return res[:top_k] if top_k else res


if __name__ == "__main__":
    print("OLD KEYWORD RESULT for:", token_keyword)
    for poi in filter_pois_by_token_keyword_old(poi_list, token_keyword):
        print(poi)
    print("\nTF-IDF EMBEDDING RESULT:")
    try:
        for poi, score in filter_pois_by_tfidf(poi_list, token_keyword):
            print(f"[score={score:.4f}] {poi}")
    except Exception as e:
        print("TF-IDF failed:", e)
        print("Run: pip install scikit-learn numpy")
    print("\nTRANSFORMER EMBEDDING RESULT:")
    try:
        r = filter_pois_by_embedding(poi_list, token_keyword, threshold=0.30)
        if not r:
            print("No match, try threshold=0.2")
        for poi, score in r:
            print(f"[score={score:.4f}] {poi}")
    except Exception as e:
        print("Skipped:", e)
        print("Run: pip install sentence-transformers scikit-learn")
    print("\nSEMANTIC DEMO:")
    for q in [["vegetarian burger"], ["fast food in Noida"], ["chicken pizza"]]:
        print(f"\nQuery: {q}")
        try:
            for poi, score in filter_pois_by_embedding(poi_list, q,
                                                       threshold=0.25, top_k=2):
                print(f"  [score={score:.4f}] pid={poi['pid']} {poi['restaurant']} | {poi['food']} | {poi['food_type']}")
        except Exception as e:
            print("  Skipped:", e)
            break

