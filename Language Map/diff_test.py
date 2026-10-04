import json, os, time, urllib.error, urllib.request
from similarity import norm, lev

MODEL = "gemma4:e2b"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

SCHEMA = {
  "type": "object",
  "properties": {
    "translation": {"type": "string"},
    "pairs": {"type": "array", "items": {
      "type": "object",
      "properties": {
        "source": {"type": "string"},
        "target": {"type": "string"},
        "relation": {"type": "string", "enum": ["same", "similar", "different", "added"]},
        "why": {"type": "string"}
      },
      "required": ["source", "target", "relation", "why"]}},
    "grammar_notes": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["translation", "pairs", "grammar_notes"]
}

EXAMPLE = """Example (Spanish -> French):
Sentence: No tengo tiempo
translation: Je n'ai pas le temps
pairs:
- source "" target "Je" relation added why "French requires a subject pronoun; Spanish drops it"
- source "No" target "ne ... pas" relation different why "French negation wraps the verb"
- source "tengo" target "ai" relation different why "tener and avoir come from different Latin verbs (tenere vs habere)"
- source "tiempo" target "temps" relation similar why "both come from Latin tempus"
grammar_notes:
- French needs an explicit subject pronoun; Spanish drops it.
- French negation wraps the verb: ne ... pas.
"""

def ask(prompt):
    body = json.dumps({"model": MODEL, "stream": False, "keep_alive": "30m", "think": False,
                   "options": {"temperature": 0, "num_ctx": 4096}, "format": SCHEMA,
                   "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL.rstrip('/')}/api/chat", body,
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(json.loads(r.read())["message"]["content"])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Ollama returned HTTP {exc.code}. Check OLLAMA_URL and confirm "
            f"the configured model '{MODEL}' is installed. {detail}"
        ) from exc

def second_opinion(pairs):
    for p in pairs:
        s, t = norm(p["source"]), norm(p["target"])
        if p["relation"] == "added" or not s or " " in s or " " in t:
            continue
        score = 1 - lev(s, t) / max(len(s), len(t))
        p["spelling"] = round(score, 2)
        ai_close = p["relation"] in ("same", "similar")
        p["flag"] = ai_close != (score >= 0.55)   # True = AI and spelling disagree
    return pairs

def diff(sentence, target="French", source="Spanish"):
    t0 = time.perf_counter()
    prompt = (f"{EXAMPLE}\nNow do the same for {source} -> {target}.\n"
              f"Sentence: {sentence}\nGive the translation, aligned word pairs "
              f"(include added words), a short 'why' for each pair, and up to 3 "
              f"specific grammar notes.")
    out = ask(prompt)
    out["pairs"] = second_opinion(out["pairs"])
    out["seconds"] = round(time.perf_counter() - t0, 1)
    out["model"] = MODEL
    return out

if __name__ == "__main__":
    print(json.dumps(diff("No quiero comer ahora"), ensure_ascii=False, indent=2))