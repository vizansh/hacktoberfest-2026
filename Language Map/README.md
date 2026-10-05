# Language Map

Language Map is a local-first language-learning prototype built for Priyansh,
who was learning Spanish with Duolingo and wanted to move toward French without
starting a completely separate path from zero.

Instead of treating languages as isolated courses, Language Map shows what
transfers across English, Latin, French, Portuguese, Spanish, and Italian:

- one-word comparisons
- root and etymology clues
- prefix and suffix notes
- sentence and word-order differences
- an “Across time” rewrite that turns formal text into current internet
  language

The goal is not to claim that every similar-looking word shares an origin. The
app labels model explanations as clues and provides a small source-linked
etymology dataset for reviewed demo words.

## Why open-weight AI

The app uses the open-weight `gemma4:e2b` model through a local Ollama
installation. This keeps prompts and learner text on the user's machine, makes
the model replaceable, and avoids requiring a hosted language API for the
prototype.

The local model is responsible for explanations and comparisons. Basic
etymology evidence is supplied separately from a reviewed, paraphrased dataset
so the model is not asked to invent historical claims from nothing.

## Features

- `/` — landing page
- `/word` — analyze one word across the prototype language group
- `/phrases` — compare a short sentence across languages
- `/time` — rewrite up to 500 characters in current Gen Z/Gen Alpha language

## Requirements

- Python 3.10+
- Ollama
- The `gemma4:e2b` model

The app can run on a CPU, but a GPU is strongly preferred for a responsive
interactive experience. Gemma inference can be noticeably slower on CPU-only
hardware, especially for phrase comparisons and longer requests.

The model is not stored in this repository.

## Setup

```bash
cd "Language Map"
python -m venv .venv
.venv/bin/pip install -r requirements.txt
ollama pull gemma4:e2b
```

On Windows/WSL, use the equivalent `.venv/bin/...` commands from the WSL
terminal. On native Windows, use `.venv\Scripts\...`.

Start the app:

```bash
.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
```

Open <http://127.0.0.1:8000/>.

## Tests

Run the small smoke suite:

```bash
python -m pytest -q tests/test_smoke.py
```

The tests check that all four pages load, empty inputs are rejected, and the
Across time input limit is enforced. They do not require a live model request.

## Etymology data

Reviewed, paraphrased entries live in `data/etymologies.json`. Each entry
includes a confidence label and a Wiktionary source link. Wiktionary's original
entries are available under CC BY-SA 4.0 and GFDL; this project stores short
paraphrases and links rather than copying full entries.

The review helper is:

```bash
python scripts/fetch_etymologies.py war
```

It prints source material for human review. It does not automatically merge
source text into the application dataset.

## Limitations

- Gemma can still make mistakes, especially with obscure etymologies.
- A model-generated explanation is not a substitute for a historical
  linguistics reference.
- The reviewed local etymology dataset is intentionally small and does not
  represent every word or language.
- The app is a prototype and currently expects Ollama to be available locally.

## Challenge context

This project was built for the Hacktoberfest 2026 DEV Challenge theme “Build
for a Friend.” The friend-focused problem is Priyansh's transition from
Spanish to French: he already knows some Romance-language patterns, but a
course restart does not show him which similarities are useful and which
differences matter.

The project should be submitted with a truthful local demo, screenshots or a
short recording, and an explanation of why local open-weight inference is
useful for privacy, cost, and experimentation.

## Demo media

The repository includes the small overview screenshot
[`Language Map.png`](./Language%20Map.png). A local screen recording is also
available as `Language Map.mp4`, but it is intentionally excluded from Git
because it is about 196 MB. Upload that recording separately to the DEV post
or a video host and link it from the submission.
