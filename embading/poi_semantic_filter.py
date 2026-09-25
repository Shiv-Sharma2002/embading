"""Semantic POI filter - ZERO dependency (no sklearn needed).
Same signature as your old function, so drop-in replacement.
Handles: 'non-veg' == 'not vegetarian' == 'non vegetarian' == 'chicken' etc.
Run: python poi_semantic_filter.py
"""
import re
from collections import Counter
from math import sqrt

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

# canonical -> synonyms (all lowercased)
SYNONYMS = {
    "non-veg": ["non-veg", "non veg", "nonveg", "not vegetarian", "not veg",
                "non vegetarian", "chicken", "mutton", "fish", "egg", "meat", "keema"],
    "veg": ["veg", "vegetarian", "veggie", "pure veg", "green"],
    "burger": ["burger", "burgers", "fast food", "mcdonald", "burger house"],
    "pizza": ["pizza", "pizzas", "italian", "cheese pizza"],
    "noida": ["noida"],
    "delhi": ["delhi"],
}

def normalize(s):
    s = str(s).lower().strip()
    s = s.replace("-", " ").replace("_", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def poi_to_text(poi, exclude=("pid", "phone", "sheet", "pincode")):
    parts = []
    for k, v in poi.items():
        if k in exclude or v is None or str(v).strip() == "":
            continue
        w = 3 if k in ("food", "food_type") else 2 if k == "restaurant" else 1
        parts += [normalize(f"{k} {v}")] * w
    return " ".join(parts)

def expand_query(token_keyword):
    """'not vegetarian' -> contains 'non-veg' canonical token."""
    q = normalize(" ".join(str(t) for t in token_keyword))
    tokens = set(q.split())
    # multi-word synonym match first
    for canon, syns in SYNONYMS.items():
        for s in syns:
            if normalize(s) in q:
                tokens.add(normalize(canon))
                tokens.update(normalize(s).split())
    return tokens

def is_nonveg_query(token_keyword):
    qraw = " ".join(str(t).lower() for t in token_keyword)
    qn = normalize(" ".join(str(t) for t in token_keyword))
    return ("not vegetarian" in qraw or "not veg" in qraw
            or "non veg" in qn or "non-veg" in qraw
            or qn in ("nonveg", "nonvegetarian"))


def is_pure_veg_query(token_keyword):
    if is_nonveg_query(token_keyword):
        return False
    qn = normalize(" ".join(str(t) for t in token_keyword))
    return qn in ("veg", "vegetarian", "veggie", "pure veg")


def cosine(a_tokens, b_tokens):
    ca, cb = Counter(a_tokens), Counter(b_tokens)
    inter = set(ca) & set(cb)
    dot = sum(ca[t] * cb[t] for t in inter)
    na = sqrt(sum(v * v for v in ca.values())) or 1
    nb = sqrt(sum(v * v for v in cb.values())) or 1
    return dot / (na * nb)


def score_one(poi, token_keyword):
    t = set(poi_to_text(poi).split())
    q = expand_query(token_keyword)
    s = cosine(q, t)
    pt = normalize(poi.get("food_type", ""))
    if is_nonveg_query(token_keyword):
        return 1.0 if pt == "non veg" else 0.0
    if is_pure_veg_query(token_keyword):
        return 1.0 if pt == "veg" else 0.0
    return s

def filter_pois_by_token_keyword(poi_list, token_keyword, threshold=0.05, top_k=None):
    """DROP-IN replacement. Same args + return (list of POIs)."""
    if not poi_list or not token_keyword:
        return []
    scored = [(score_one(p, token_keyword), p) for p in poi_list]
    scored = [(s, p) for s, p in scored if s >= threshold]
    scored.sort(key=lambda x: x[0], reverse=True)
    if top_k:
        scored = scored[:top_k]
    return [p for _, p in scored]

def filter_with_scores(poi_list, token_keyword, threshold=0.05, top_k=None):
    if not poi_list or not token_keyword:
        return []
    out = [(p, round(score_one(p, token_keyword), 4)) for p in poi_list]
    out = [(p, s) for p, s in out if s >= threshold]
    out.sort(key=lambda x: x[1], reverse=True)
    return out[:top_k] if top_k else out


if __name__ == "__main__":
    tests = [["non-veg"], ["not vegetarian"], ["non vegetarian"],
             ["veg"], ["vegetarian"], ["Burger"], ["fast food in Noida"]]
    for tk in tests:
        print(f"\nQuery: {tk}")
        print("-" * 50)
        res = filter_with_scores(poi_list, tk)
        if not res:
            print("  No match")
        for poi, score in res:
            print(f"  [score={score}] pid={poi['pid']} {poi['restaurant']} | {poi['food']} | {poi['food_type']}")
