import diff_test, json

SENTENCES = ["No quiero comer ahora", "La casa grande es muy bonita", "Me gusta leer libros por la noche"]

for model in ["gemma4:e4b"]:
    diff_test.MODEL = model
    for s in SENTENCES:
        out = diff_test.diff(s)
        print(f"\n=== {model} | {s} | {out['seconds']}s")
        print(out["translation"])
        for p in out["pairs"]:
            print("  ", p["source"], "->", p["target"], p["relation"], p.get("flag", ""))   