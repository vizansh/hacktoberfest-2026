import json, os, urllib.error, urllib.request
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import diff_test

diff_test.MODEL = os.environ.get("LM_MODEL", "gemma4:e2b")
app = FastAPI()
CACHE = "cache.json"
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}

@app.get("/api/diff")
def api_diff(sentence: str, target: str = "French"):
    key = f"{diff_test.MODEL}|{target}|{sentence.strip().lower()}"
    try:
        if key not in cache:
            cache[key] = diff_test.diff(sentence.strip(), target)
            json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        return cache[key]
    except Exception as e:
        return JSONResponse({"error": f"Could not reach the local model: {e}"}, status_code=503)

import similarity

def _load(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default

LEX = _load("data/lexicon.json", {})
ETYMOLOGIES = _load("data/etymologies.json", {})
TREES = _load("data/trees.json", {}).get("language_families", {})
NAMES = {"la": "Latin", "pt": "Portuguese", "it": "Italian",
         "fr": "French", "es": "Spanish", "en": "English"}
LANGUAGES = {
    "en": "English", "la": "Latin", "fr": "French", "pt": "Portuguese",
    "es": "Spanish", "it": "Italian",
}

WORD_SCHEMA = {
    "type": "object",
    "properties": {
        "input": {"type": "string"},
        "detected_language": {"type": "string"},
        "concept": {"type": "string"},
        "translations": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "language": {"type": "string"},
                "word": {"type": "string"},
                "relation": {"type": "string"},
                "root": {"type": "string"},
                "etymology": {"type": "string"},
                "prefix_suffix": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["language", "word", "relation", "root",
                         "etymology", "prefix_suffix", "explanation"],
        }},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["input", "detected_language", "concept", "translations",
                 "notes"],
}

WORD_PROMPT = """You are the word-analysis engine for Language Map.
Analyze the one word below and compare it across these languages represented
in our language tree: English, Latin, French, Portuguese, Spanish, and Italian.

Return only JSON matching the supplied schema.
Rules:
- Detect the input language; do not assume Spanish.
- Give one useful translation or equivalent for each language you can
  confidently handle. Do not invent obscure forms.
- For each result, explain whether the root appears related, different, or
  uncertain. Spelling similarity is not proof of shared etymology.
- Explain the likely etymology of the root word, including an older source
  language or reconstructed root when one is known. If uncertain, say so.
- Identify prefix, root, and suffix only when the analysis is defensible.
  Explain what each affix does in that language. Otherwise say "uncertain".
- Etymology and morphology must be described as clues, not absolute facts.
- Keep notes short and useful to a learner.

Word: """

PHRASE_SCHEMA = {
    "type": "object",
    "properties": {
        "input": {"type": "string"},
        "detected_language": {"type": "string"},
        "translations": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "language": {"type": "string"},
                "sentence": {"type": "string"},
                "word_changes": {"type": "string"},
                "root_etymology": {"type": "string"},
                "prefix_suffix_changes": {"type": "string"},
                "structure_change": {"type": "string"},
                "root_words": {"type": "array", "items": {"type": "string"}},
                "structure_words": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["language", "sentence", "word_changes",
                         "root_etymology", "prefix_suffix_changes",
                         "structure_change", "root_words", "structure_words"],
        }},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["input", "detected_language", "translations", "notes"],
}

PHRASE_PROMPT = """You are the sentence-comparison engine for Language Map.
Analyze the short sentence below across English, Latin, French, Portuguese,
Spanish, and Italian.

Return only JSON matching the supplied schema.
Rules:
- Detect the input language; do not assume Spanish.
- Translate the sentence naturally into each comparison language.
- Explain only meaningful word or root changes, not every matching word.
- Explain likely root etymology when useful, and label uncertain claims.
- Explain prefix or suffix changes only when they affect the sentence.
- Explain changes in word order, agreement, articles, pronouns, negation,
  or other sentence structure.
- Return root_words as the exact translated words whose roots differ from the
  input sentence. Return structure_words as exact words involved in a
  meaningful structure change. Use empty arrays when there is no clear change.
- Do not claim that similar spelling proves shared etymology.
- Keep each explanation short enough for a learner to read.

Sentence: """

TIME_SCHEMA = {
    "type": "object",
    "properties": {"modern_text": {"type": "string"}},
    "required": ["modern_text"],
}

TIME_PROMPT = """Rewrite the paragraph below in clear, natural current Gen Z /
Gen Alpha internet language. Preserve the meaning and important details.
Use present-day expressions only when they fit the meaning and audience.
Useful examples include "rizz" for charm, "cooking" for doing well,
"locked in" for focused, "aura" for presence or cool factor, "ate" for
excellent execution, "no cap" for honesty, and "touch grass" for taking a
break from the internet. These are examples, not a checklist: do not force
slang into every sentence, stack expressions, or make the rewrite sound like
a parody. Avoid outdated or harmful stereotypes, and do not add facts,
insults, or excessive slang. Keep it readable and return only JSON matching
the schema.

Paragraph: """

def _gemma_word(word):
    verified = []
    normalized = similarity.norm(word)
    for key, entry in ETYMOLOGIES.items():
        if similarity.norm(key) == normalized:
            verified.append(entry)
    evidence = ""
    if verified:
        evidence = (
            "\nVerified reference context. Treat this as evidence, not as "
            "something to contradict without a reason:\n"
            + json.dumps(verified, ensure_ascii=False)
            + "\n"
        )
    body = json.dumps({
        "model": diff_test.MODEL,
        "stream": False,
        "think": False,
        "format": WORD_SCHEMA,
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "user", "content": WORD_PROMPT + word + evidence}],
    }).encode()
    request = urllib.request.Request(
        f"{diff_test.OLLAMA_URL.rstrip('/')}/api/chat",
        body,
        {"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read())
            return json.loads(payload["message"]["content"])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Ollama returned HTTP {exc.code} for model '{diff_test.MODEL}'. "
            f"Check that the model is available. {detail}"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {diff_test.OLLAMA_URL}. "
            "Start Ollama and try again."
        ) from exc
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Ollama returned an invalid word-analysis response.") from exc

def _gemma_phrase(sentence):
    body = json.dumps({
        "model": diff_test.MODEL,
        "stream": False,
        "think": False,
        "format": PHRASE_SCHEMA,
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "user", "content": PHRASE_PROMPT + sentence}],
    }).encode()
    request = urllib.request.Request(
        f"{diff_test.OLLAMA_URL.rstrip('/')}/api/chat",
        body,
        {"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read())
            return json.loads(payload["message"]["content"])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Ollama returned HTTP {exc.code} for model '{diff_test.MODEL}'. "
            f"Check that the model is available. {detail}"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {diff_test.OLLAMA_URL}. "
            "Start Ollama and try again."
        ) from exc
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Ollama returned an invalid phrase-analysis response.") from exc

def _gemma_time(text):
    body = json.dumps({
        "model": diff_test.MODEL,
        "stream": False,
        "think": False,
        "format": TIME_SCHEMA,
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "user", "content": TIME_PROMPT + text}],
    }).encode()
    request = urllib.request.Request(
        f"{diff_test.OLLAMA_URL.rstrip('/')}/api/chat",
        body,
        {"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read())
            return json.loads(payload["message"]["content"])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Ollama returned HTTP {exc.code} for model '{diff_test.MODEL}'. "
            f"Check that the model is available. {detail}"
        ) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {diff_test.OLLAMA_URL}. "
            "Start Ollama and try again."
        ) from exc
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Ollama returned an invalid rewrite response.") from exc

def _word_result(word, source, level):
    normalized = similarity.norm(word)
    matches = []
    for concept, translations in LEX.items():
        for code, value in translations.items():
            if similarity.norm(value) == normalized and code == source:
                matches.append((concept, translations))
    if not matches:
        return None

    concept, translations = matches[0]
    entries = []
    for code, name in LANGUAGES.items():
        if code not in translations:
            continue
        value = translations[code]
        score = round(1 - similarity.lev(normalized, similarity.norm(value)) /
                      max(len(normalized), len(similarity.norm(value))), 2)
        relation = "same root pattern" if score >= 0.7 else "different root pattern"
        entries.append({"code": code, "language": name, "word": value,
                        "score": score, "relation": relation})

    notes = [
        f"Concept: {concept.replace('_', ' ')}.",
        "Higher spelling similarity is a useful clue, not proof of shared etymology."
    ]
    if level == "starter":
        notes = notes[:1]
    return {"input": word, "source": source, "source_language": LANGUAGES[source],
            "level": level, "concept": concept, "translations": entries,
            "notes": notes, "source": "local lexicon"}

@app.get("/api/languages")
def api_languages():
    return [{"code": code, "name": name} for code, name in LANGUAGES.items()
            if any(code in row for row in LEX.values())]

@app.get("/api/word")
def api_word(word: str):
    word = word.strip()
    if not word:
        return JSONResponse({"error": "Enter one word to analyze."}, status_code=400)
    try:
        result = _gemma_word(word)
    except RuntimeError as exc:
        return JSONResponse({"error": str(exc)}, status_code=503)
    result["source"] = diff_test.MODEL
    return result

@app.get("/api/phrase")
def api_phrase(sentence: str):
    sentence = sentence.strip()
    if not sentence:
        return JSONResponse({"error": "Enter a short sentence to analyze."}, status_code=400)
    try:
        result = _gemma_phrase(sentence)
    except RuntimeError as exc:
        return JSONResponse({"error": str(exc)}, status_code=503)
    result["source"] = diff_test.MODEL
    return result

@app.get("/api/time")
def api_time(text: str):
    text = text.strip()
    if not text:
        return JSONResponse({"error": "Enter a paragraph to rewrite."}, status_code=400)
    if len(text) > 500:
        return JSONResponse({"error": "Keep the paragraph under 500 characters."}, status_code=413)
    try:
        result = _gemma_time(text)
    except RuntimeError as exc:
        return JSONResponse({"error": str(exc)}, status_code=503)
    result["source"] = diff_test.MODEL
    return result

@app.get("/api/map")
def api_map(focus: str = "es"):
    rank = sorted(({"name": n, "score": round(similarity.closeness(focus, c, LEX), 2)}
                   for c, n in NAMES.items()), key=lambda x: -x["score"])
    return {"tree": TREES, "ranking": rank}

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/word")
def word_page():
    return FileResponse("static/word.html")

@app.get("/phrases")
def phrases_page():
    return FileResponse("static/phrases.html")

@app.get("/time")
def time_page():
    return FileResponse("static/time.html")