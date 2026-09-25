"""Test for poi_semantic_filter.py - zero dependency."""
from poi_semantic_filter import filter_pois_by_token_keyword as f, filter_with_scores as fs, poi_list

def pids(res):
    return sorted([p["pid"] for p in res])

print("TEST 1: ['non-veg'] -> pid 2 only")
r = f(poi_list, ["non-veg"])
print(" ", pids(r)); assert pids(r) == [2]; print("  PASS")

print("TEST 2: ['not vegetarian'] -> pid 2 only (YOUR NEW CASE)")
r = f(poi_list, ["not vegetarian"])
print(" ", pids(r)); assert pids(r) == [2]; print("  PASS")

print("TEST 3: ['non vegetarian'] -> pid 2 only")
r = f(poi_list, ["non vegetarian"])
print(" ", pids(r)); assert pids(r) == [2]; print("  PASS")

print("TEST 4: ['veg'] -> pid 1,3 (NOT 2 - old code bug fixed)")
r = f(poi_list, ["veg"])
print(" ", pids(r)); assert pids(r) == [1, 3]; print("  PASS")

print("TEST 5: ['vegetarian'] -> pid 1,3")
r = f(poi_list, ["vegetarian"])
print(" ", pids(r)); assert pids(r) == [1, 3]; print("  PASS")

print("TEST 6: ['Burger'] -> pid 1,3")
r = f(poi_list, ["Burger"])
print(" ", pids(r)); assert pids(r) == [1, 3]; print("  PASS")

print("TEST 7: ['fast food in Noida'] ranks pid 1 first")
r = fs(poi_list, ["fast food in Noida"])
for poi, s in r: print(f"   [score={s}] pid={poi['pid']}")
assert r[0][0]["pid"] == 1; print("  PASS")

print("TEST 8: empty -> []")
assert f(poi_list, []) == [] and f([], ["veg"]) == []; print("  PASS")

print("\nALL 8 TESTS PASSED")
