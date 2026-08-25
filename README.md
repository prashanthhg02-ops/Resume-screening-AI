# Shortlist

A local AI/ML resume screening workspace. Paste a job description, upload PDF or TXT resumes, and get an explainable ranked shortlist.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py app.py
```

Open `http://127.0.0.1:5000` in a browser.

## How scoring works

The app extracts text from each resume, detects skills from a small editable vocabulary, and calculates TF-IDF cosine similarity between the job description and each resume. The final score combines semantic similarity (55%) with overlap of explicitly requested skills (45%). This is decision support, not an automated hiring decision; review the underlying resumes and consider fairness and accessibility in your process.

## Structure

- `app.py`: Flask server and screening pipeline
- `templates/index.html`: screening dashboard
- `static/styles.css`: responsive visual system
- `static/app.js`: upload, API, and results interactions
