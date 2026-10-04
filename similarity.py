import json, unicodedata

def norm(w):
    return "".join(c for c in unicodedata.normalize("NFD", w.lower())
                   if unicodedata.category(c) != "Mn")

def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j-1] + 1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]

def closeness(lang_a, lang_b, lex):
    scores = []
    for word in lex.values():
        if lang_a in word and lang_b in word:
            a, b = norm(word[lang_a]), norm(word[lang_b])
            scores.append(1 - lev(a, b) / max(len(a), len(b)))
    return sum(scores) / len(scores)

if __name__ == "__main__":
    lex = json.load(open("data/lexicon.json", encoding="utf-8"))
    for other in ["pt", "it", "fr"]:
        print("es ->", other, round(closeness("es", other, lex), 2))