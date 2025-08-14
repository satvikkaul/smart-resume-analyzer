from fastapi.testclient import TestClient
from main import app
c = TestClient(app)

def test_lexicon_cosine_and_coverage_basic():
    files = {
        "resume": ("r.txt", b"python fastapi tensorflow", "text/plain"),
        "job_description": ("j.txt", b"Looking for FastAPI and TensorFlow", "text/plain"),
    }
    r = c.post("/score", files=files)
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["cosine_similarity"] <= 1.0
    assert 0.0 <= data["coverage"] <= 1.0
    assert "fastapi" in " ".join(data["matched"])

def test_docx_tables_extraction(tmp_path):
    import docx as _docx
    p = tmp_path / "resume.docx"
    d = _docx.Document()
    t = d.add_table(rows=1, cols=2)
    t.rows[0].cells[0].text = "python"
    t.rows[0].cells[1].text = "fastapi"
    d.save(p)
    r = c.post("/analyze", files={
        "resume": ("resume.docx", p.read_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "job_description": ("j.txt", b"python", "text/plain"),
    })
    assert r.status_code == 200
    assert "python" in r.json()["resume_preview"].lower()
