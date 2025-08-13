# Smart Resume Analyzer

Smart Resume Analyzer that not only matches resumes to job descriptions based on keywords, but also reads the tone, evaluates alignment with job traits, and suggests actionable rewrites using rule-based NLP and optional LLM support.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Optional: a virtual environment tool such as `venv` or `conda`

## Installation

```bash
git clone <repo-url>
cd smart-resume-analyzer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running the FastAPI server

1. Ensure dependencies are installed and any required environment variables are set.
2. Start the development server:

```bash
uvicorn main:app --reload
```

3. The API is served at `http://localhost:8000` with interactive docs available at `/docs`.

## Environment Variables

- `ADMIN_TOKEN` – secret token used to secure the `/admin/reload-skills` endpoint.

Example:

```bash
export ADMIN_TOKEN=my-secret-token
```

## API Usage

- `POST /analyze` – upload `resume` and `job_description` files to extract raw text.
- `POST /score` – upload `resume` and `job_description` files to receive keyword matching and similarity scores.
- `POST /admin/reload-skills` – reload skill configuration. Requires header `X-Admin-Token: <ADMIN_TOKEN>`.

Example curl request:

```bash
curl -X POST http://localhost:8000/score \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=@/path/to/jd.txt"
```

## Launching the UI

A simple React interface lives in the `smart-resume-ui` folder.

```bash
cd smart-resume-ui
npm install
npm run dev
```

The UI will be available at `http://localhost:5173` (default Vite port) and expects the FastAPI server to be running locally.

