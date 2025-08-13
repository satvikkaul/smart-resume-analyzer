const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function analyzeFiles(resumeFile, jdFile) {
  const fd = new FormData();
  fd.append("resume", resumeFile);
  fd.append("job_description", jdFile);

  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: fd
  });
  if (!res.ok) {
    const msg = await safeErr(res);
    throw new Error(`Analyze failed: ${msg}`);
  }
  return res.json();
}

export async function scoreFiles(resumeFile, jdFile) {
  const fd = new FormData();
  fd.append("resume", resumeFile);
  fd.append("job_description", jdFile);

  const res = await fetch(`${API_BASE}/score`, {
    method: "POST",
    body: fd
  });
  if (!res.ok) {
    const msg = await safeErr(res);
    throw new Error(`Score failed: ${msg}`);
  }
  return res.json();
}

async function safeErr(res) {
  try {
    const data = await res.json();
    return data?.detail || res.statusText;
  } catch {
    return res.statusText;
  }
}
