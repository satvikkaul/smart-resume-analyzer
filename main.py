from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import fitz
import re 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_BYTES = 5 * 1024 * 1024  # 5 MB per file for v1

async def _read_bytes(f: UploadFile) -> bytes:
    # Reset pointer, read, enforce size, and reset again for safety
    await f.seek(0)
    data = await f.read()
    await f.seek(0)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (>5MB)")
    return data

async def extract_text(file: UploadFile) -> str:
    name = (file.filename or "").lower()
    data = await _read_bytes(file)

    if name.endswith(".txt"):
        # Decode text files defensively
        return data.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        # Iterate all pages. Your original code returned after page 1.
        text_chunks = []
        try:
            with fitz.open(stream=data, filetype="pdf") as doc:
                for page in doc:
                    text_chunks.append(page.get_text())
        except fitz.FileDataError:
            raise HTTPException(status_code=400, detail="Invalid PDF")
        return "\n".join(text_chunks)

    # Add .docx later; keep v1 narrow to reduce moving parts
    raise HTTPException(status_code=415, detail="Unsupported file type. Use .txt or .pdf for now.")

@app.post("/analyze")
async def analyze_files(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    resume_text = await extract_text(resume)
    jd_text = await extract_text(job_description)

    return {
        "resume_preview": resume_text[:400],
        "jd_preview": jd_text[:400],
        "resume_chars": len(resume_text),
        "jd_chars": len(jd_text),
    }

STOPWORDS = {
    "and","or","the","a","an","to","of","in","for","with","on","at","by","from",
    "is","are","be","as","this","that","it","you","we","they","our","their"
}

def normalize(s: str) -> str:
    s = s.lower()
    # remove emails/phones/urls to avoid false matches
    s = re.sub(r"\S+@\S+", " ", s)
    s = re.sub(r"\b(?:\+?\d[\d\-\s]{7,}\d)\b", " ", s)
    s = re.sub(r"https?://\S+|www\.\S+", " ", s)
    s = re.sub(r"[^a-z0-9\+\#\.\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize_words(s: str):
    return re.findall(r"[a-z0-9\+\#\.]{2,}", s)

def extract_candidate_keywords(jd_text: str) -> list[str]:
    tokens = [t for t in tokenize_words(jd_text) if t not in STOPWORDS]
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]
    return [w for w,_ in top]

def keyword_coverage(resume_text: str, jd_text: str):
    jd_keys = extract_candidate_keywords(jd_text)
    resume_tokens = set(tokenize_words(resume_text))
    matched = [k for k in jd_keys if k in resume_tokens]
    coverage = round(len(matched) / max(1, len(jd_keys)), 3)
    return coverage, matched, [k for k in jd_keys if k not in resume_tokens][:20]

def tfidf_cosine(resume_text: str, jd_text: str) -> float:
    # ngram_range=(1,2) helps match “data analysis” vs “analysis”
    vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
    X = vectorizer.fit_transform([jd_text, resume_text])
    # cosine between JD (row 0) and Resume (row 1)
    cos = cosine_similarity(X[0], X[1])[0][0]
    return float(round(cos, 3))

@app.post("/score")
async def score(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    resume_raw = await extract_text(resume)
    jd_raw = await extract_text(job_description)

    # normalize for both methods
    resume_text = normalize(resume_raw)
    jd_text = normalize(jd_raw)

    # keyword coverage
    coverage, matched, missing = keyword_coverage(resume_text, jd_text)

    # tf-idf cosine similarity
    cosine = tfidf_cosine(resume_text, jd_text)

    # simple composite: weight semantic higher than coverage
    overall = round(0.65 * cosine + 0.35 * coverage, 3)

    return {
        "overall_score": overall,
        "cosine": cosine,
        "coverage": coverage,
        "matched_keywords": matched,
        "missing_keywords_sample": missing,
        "resume_chars": len(resume_raw),
        "jd_chars": len(jd_raw)
    }