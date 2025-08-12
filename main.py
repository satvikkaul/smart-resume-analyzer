from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles

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

# --- normalization/tokenization ---
def normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\S+@\S+", " ", s)                            # emails
    s = re.sub(r"\b(?:\+?\d[\d\-\s]{7,}\d)\b", " ", s)        # phones
    s = re.sub(r"https?://\S+|www\.\S+", " ", s)              # urls
    s = re.sub(r"[^a-z0-9\+\#\.\-\/\s]", " ", s)              # keep + # . - /
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize_words(s: str):
    return re.findall(r"[a-z0-9\+\#\.\-\/]{2,}", s)

def extract_candidate_keywords(jd_text: str) -> list[str]:
    tokens = [t for t in tokenize_words(jd_text) if t not in STOPWORDS]
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:50]
    return [w for w,_ in top]

def keyword_match(resume_text: str, jd_text: str):
    jd_keys = extract_candidate_keywords(jd_text)
    resume_tokens = set(tokenize_words(resume_text))
    matched = [k for k in jd_keys if k in resume_tokens]
    coverage = round(len(matched) / max(1, len(jd_keys)), 3)
    # Call the tfidf_cosine function to get the semantic score
    cosine_similarity_score = tfidf_cosine(resume_text, jd_text)
    
    # simple composite: weight semantic higher than coverage
    overall_score = round(0.65 * cosine_similarity_score + 0.35 * coverage, 3)

    return {
        "overall_score": overall_score,
        "cosine_similarity": cosine_similarity_score,
        "coverage": coverage,
        "matched": matched,
        "missing_sample": [k for k in jd_keys if k not in resume_tokens][:20]
    }

# --- tfidf with guard and matching token pattern ---
def tfidf_cosine(resume_text: str, jd_text: str) -> float:
    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=False,                               # already normalized
            token_pattern=r"[a-z0-9\+\#\.\-\/]{2,}",
            stop_words=None                                # optional: 'english'
        )
        tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
        cos = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
        return float(round(cos, 3))
    except ValueError:
        # e.g., empty vocabulary after normalization
        return 0.0

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


    score_data = keyword_match(resume_text, jd_text)
    
    # Return the entire dictionary of scores and data.
    return score_data