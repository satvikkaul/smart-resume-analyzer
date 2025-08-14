from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_docs_alive():
    r = client.get("/docs")
    assert r.status_code == 200

def test_score_txt_roundtrip():
    files = {
        "resume": ("r.txt", b"python fastapi tensorflow", "text/plain"),
        "job_description": ("j.txt", b"fastapi and tensorflow preferred", "text/plain"),
    }
    r = client.post("/score", files=files)
    assert r.status_code == 200
    data = r.json()
    # basic shape
    for k in ["overall_score", "cosine_similarity", "coverage", "matched", "missing_sample"]:
        assert k in data
