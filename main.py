from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import fitz

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def extract_text(file: UploadFile)->str:
        
        if file.filename.endswith(".txt"):
            return file.file.read().decode("utf-8")

        elif file.filename.endswith(".pdf"):
                with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
                    text = ""
                    for page in doc:
                            text += page.get_text()
                            return text
                    
        else:
            return "unsupported file type"

      


@app.post("/analyze")
async def analyze_files(
    resume: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
      resume_text = extract_text(resume)
      jd_text = extract_text(job_description)
      
      return {
        "resume_preview": resume_text[:400],
        "jd_preview": jd_text[:400],
        "resume_char": len(resume_text),
        "jd_chars": len(jd_text)
    }

