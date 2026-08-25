from pathlib import Path
import re

from flask import Flask, jsonify, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

SKILL_VOCABULARY = {
    "python", "javascript", "typescript", "java", "c++", "sql", "html", "css",
    "react", "vue", "angular", "node.js", "flask", "django", "fastapi", "aws",
    "azure", "gcp", "docker", "kubernetes", "terraform", "git", "linux", "excel",
    "tableau", "power bi", "machine learning", "deep learning", "nlp", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "rest api", "graphql", "agile",
    "scrum", "project management", "communication", "leadership", "figma", "research",
}


def extract_text(upload):
    if not upload or not upload.filename:
        return ""
    if upload.filename.lower().endswith(".pdf"):
        if PdfReader is None:
            raise ValueError("PDF support is unavailable. Install the requirements first.")
        reader = PdfReader(upload.stream)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return upload.read().decode("utf-8", errors="ignore")


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def skills_in(text):
    normalized = normalize(text)
    return sorted(skill for skill in SKILL_VOCABULARY if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", normalized))


def screen_resume(resume_text, job_description):
    resume_clean = normalize(resume_text)
    job_clean = normalize(job_description)
    if not resume_clean or not job_clean:
        return {"score": 0, "matched_skills": [], "missing_skills": [], "similarity": 0}

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([job_clean, resume_clean])
    similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    job_skills = set(skills_in(job_clean))
    resume_skills = set(skills_in(resume_clean))
    matched = sorted(job_skills & resume_skills)
    missing = sorted(job_skills - resume_skills)
    skill_ratio = len(matched) / len(job_skills) if job_skills else similarity
    score = round(min(99, max(1, similarity * 55 + skill_ratio * 45)))
    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "similarity": round(similarity * 100),
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/screen")
def screen():
    job_description = request.form.get("job_description", "")
    files = request.files.getlist("resumes")
    if not job_description.strip() or not files:
        return jsonify({"error": "Add a job description and at least one resume."}), 400

    results = []
    for upload in files:
        try:
            text = extract_text(upload)
            analysis = screen_resume(text, job_description)
            results.append({"name": upload.filename, "size": len(text), **analysis})
        except ValueError as error:
            return jsonify({"error": str(error)}), 400

    results.sort(key=lambda item: item["score"], reverse=True)
    for index, result in enumerate(results, 1):
        result["rank"] = index
        result["status"] = "Strong match" if result["score"] >= 75 else "Review" if result["score"] >= 50 else "Low match"
    return jsonify({"results": results, "count": len(results)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
