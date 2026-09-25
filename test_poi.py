"""Quick test for poi_embedding_filter.py - no transformer needed."""
from poi_embedding_filter import (
    poi_to_text, query_to_text,
    filter_pois_by_token_keyword_old,
    filter_pois_by_tfidf, poi_list
)

print("TEST 1: poi_to_text")
t = poi_to_text(poi_list[0])
print(" ", t)
assert "Burger" in t and "12345" not in t, "exclude phone failed"
print("  PASS")

print("\nTEST 2: old keyword ['non-veg'] should return pid=2 only")
r = filter_pois_by_token_keyword_old(poi_list, ["non-veg"])
print(" ", r)
assert len(r) == 1 and r[0]["pid"] == 2
print("  PASS")

print("\nTEST 3: old keyword ['veg'] bug demo - matches all 3 (even non-veg)")
r = filter_pois_by_token_keyword_old(poi_list, ["veg"])
print("  matched pids:", [p["pid"] for p in r])
print("  (This is WHY you need embeddings)")

print("\nTEST 4: TF-IDF ['non-veg'] should rank pid=2 first")
try:
    res = filter_pois_by_tfidf(poi_list, ["non-veg"], threshold=0.0)
    for poi, s in res:
        print(f"  [score={s:.4f}] pid={poi['pid']}")
    assert res[0][0]["pid"] == 2, "pid 2 should be top"
    print("  PASS")
except Exception as e:
    print("  FAIL - install sklearn:", e)

print("\nTEST 5: TF-IDF ['Burger'] should return pid 1,3")
try:
    res = filter_pois_by_tfidf(poi_list, ["Burger"], threshold=0.1)
    print("  matched pids:", [p["pid"] for p, _ in res])
    assert set(p["pid"] for p, _ in res) == {1, 3}
    print("  PASS")
except Exception as e:
    print("  FAIL:", e)

print("\nTEST 6: TF-IDF empty query returns []")
assert filter_pois_by_tfidf(poi_list, [], threshold=0.0) == []
print("  PASS")

print("\nALL BASIC TESTS DONE")
