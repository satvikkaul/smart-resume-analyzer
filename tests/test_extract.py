from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_invalid_pdf():
  r = client.post("/analyze", files={
    "resume": ("bad.pdf", b"%PDF-1.4 garbage", "application/pdf"),
    "job_description": ("j.txt", b"x", "text/plain"),
  })
  assert r.status_code in (400, 415)

def test_docx_tables(tmp_path):
  import docx, io
  p = tmp_path/"a.docx"
  d = docx.Document()
  t = d.add_table(rows=1, cols=2); t.rows[0].cells[0].text="python"; t.rows[0].cells[1].text="fastapi"
  d.save(p)
  r = client.post("/analyze", files={
    "resume": ("a.docx", p.read_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "job_description": ("j.txt", b"python fastapi", "text/plain"),
  })
  assert r.status_code == 200
  assert "python" in r.json()["resume_preview"].lower()
