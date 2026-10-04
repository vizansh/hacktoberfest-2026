import json, time, urllib.request

def run(model, prompt):
    body = {"model": model, "stream": False, "think": False, "keep_alive": "30m",
            "options": {"temperature": 0, "num_ctx": 2048},
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    t0 = time.perf_counter()
    r = json.loads(urllib.request.urlopen(req, timeout=600).read())
    n = r.get("eval_count", 0)
    tps = n / max(r.get("eval_duration", 1) / 1e9, 1e-9)
    return r["message"]["content"].strip(), time.perf_counter() - t0, n, tps

SENTENCES = ["No quiero comer ahora", "La casa grande es muy bonita", "Me gusta leer libros por la noche"]
for model in ["gemma4:e2b"]:
    run(model, "Say hi")   # warm-up so loading time doesn't count
    for s in SENTENCES:
        out, dt, n, tps = run(model, f"Translate to French. Reply with only the translation.\n{s}")
        print(f"{model} | {dt:.1f}s | {n} tokens | {tps:.1f} tok/s | {out}")