# NLP Project — Interview Q&A Cheat Sheet

---

### 1. What is this project?

It is a web app that provide NLP(Natural Language Processing) Services like (Sentiment Analysis , Text Clasification and Name Entity Regnisition) i have used Hugging Face api to achive this and also use streamlit to create a ui for users

---

### 2. What tech did you use?

- Python (backend logic)
- Hugging Face Inference API (NER, sentiment, classification models)
- Streamlit (UI)
- JSON file as a simple user database
- python-dotenv (to keep the API key out of the code)

---

### 3. Did you build the whole thing yourself?

"I designed the app structure, the login/register system, the JSON database, and the API integration myself. For the Streamlit UI, I used Claude AI to help me build it faster — I gave it exact requirements and reviewed/tested everything before using it. I treat it like any other dev tool, the same way people use GitHub Copilot."

Don't hide this. Say it plainly and move on — recruiters care more about whether you understand your own project.

---

### 4. Walk me through the file structure.

- `streamlit_app.py` — the Streamlit UI and glue code (login screens, task pages, calling the backend functions)
- `app.py` — the original simple CLI version (registration + tool selection), kept from before the UI existed
- `ner.py`, `sn.py`, `TC.py` — one file per NLP task, each a Hugging Face API wrapper (NER, Sentiment, Text Classification)
- `nlp/` — a package with some helper/consolidated copies, used while cleaning up the code
- `Database.json` — simple local JSON store for registered users (demo-level DB)
- `.env` — environment variables, not committed to GitHub, holds `HF_TOKEN` (Hugging Face API key)
- `requirements.txt` — Python dependencies
- `venv/` — virtual environment, excluded from version control

Why split it this way: each NLP task is isolated in its own file so it's easy to test, replace, or extend individually. The UI layer (`streamlit_app.py`) just imports and calls these — it doesn't duplicate any logic.

---

### 5. How does login/register work?

Register saves name, email, phone, password into a JSON file, keyed by email. Login checks if the email exists and the password matches. Simple, no external database — good enough for a small project.

---

### 6. What is NER and how does it work in your project?

NER = Named Entity Recognition — finds names of people, organizations, locations, etc. in text. I send the text to a Hugging Face NER model via API, get back words with entity types (PER, ORG, LOC), and merge broken sub-word pieces (like "New" + "##York") back into one word before showing the result.

---

### 7. What is Sentiment Analysis in your project?

It sends text to a Hugging Face sentiment model, which returns a label (positive/negative) and a confidence score, which I show as a percentage.

---

### 8. What is Text Classification here?

It's "zero-shot" classification — you give it text plus custom category labels (like Sports, Politics, Technology, Business), and the model scores how well the text matches each one, without being specifically trained on those categories.

---

### 9. Why Streamlit and not Flask/Django?

Streamlit is much faster to build a working UI with, especially for data/ML-facing apps — less boilerplate, no separate frontend code needed. Good fit for a quick, functional project like this.

---

### 10. What are the security weaknesses, and how would you fix them?

- Passwords are stored in plain text right now — in production I'd hash them with bcrypt.
- JSON file isn't a real database — I'd move to SQLite or PostgreSQL if this needed to scale.
- API key is in `.env`, kept out of GitHub — that part's already handled correctly.

---

### 11. What was the hardest part?

Merging the sub-word tokens from the NER model output into full words/entities was the fiddly part — the model breaks words into pieces and I had to stitch them back together correctly.

---

### 12. What would you add next?

- Text Summarization (already planned — `summarization.py` placeholder exists)
- Password hashing
- A real database
- Deploying it live (Streamlit Community Cloud or Hugging Face Spaces)

---

### 13. Why did you pick this project?

Simple honest answer: "I wanted a project that touches multiple core NLP tasks in one place, and forces me to handle real API integration, error handling, and a basic auth system — not just a single notebook demo."

---

## Golden rule
If they ask something you genuinely don't know the deep internals of (e.g. exact model architecture behind Hugging Face's pipeline) — it's fine to say "I used it via the Hugging Face API, I didn't train the model myself, but I understand what it's doing at a high level." Honesty > bluffing.
