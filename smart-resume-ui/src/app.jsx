import { useState } from "react";
import FileDrop from "./components/FileDrop.jsx";
import MetricBar from "./components/MetricBar.jsx";
import { analyzeFiles, scoreFiles } from "./api.js";
import "./app.css";

export default function App() {
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState(null);

  const [analyze, setAnalyze] = useState(null);
  const [score, setScore] = useState(null);

  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [loadingScore, setLoadingScore] = useState(false);
  const [error, setError] = useState("");
  const [resetTrigger, setResetTrigger] = useState(false);

  // Enable only after a run (analyze or score) AND files selected
  const canDownload = Boolean(resume && jd && (score || analyze));
  const downloadPayload = score ?? analyze; // prefer score JSON if available

  const canRun = resume && jd;
    
  async function onAnalyze() {
    setError(""); setAnalyze(null); setLoadingAnalyze(true);
    try {
      const data = await analyzeFiles(resume, jd);
      setAnalyze(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingAnalyze(false);
    }
  }

  async function onScore() {
    setError(""); setScore(null); setLoadingScore(true);
    try {
      const data = await scoreFiles(resume, jd);
      setScore(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingScore(false);
    }
  }

  return (
    <div className="page">
      <h1>Smart Resume Analyzer</h1>
      

      <div className="grid">
        <FileDrop
          label="Resume (.pdf / .txt / .docx)"
          accept=".pdf,.txt,.docx"
          onFile={setResume}
          reset={resetTrigger}  
        />
        <FileDrop
          label="Job Description (.pdf / .txt / .docx)"
          accept=".pdf,.txt,.docx"
          onFile={setJd}
          reset={resetTrigger}  
        />
      </div>

      <div className="actions">
        <button disabled={!canRun || loadingAnalyze} onClick={onAnalyze}>
          {loadingAnalyze ? "Analyzing..." : "Analyze"}
        </button>
        <button disabled={!canRun || loadingScore} onClick={onScore}>
          {loadingScore ? "Scoring..." : "Score"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {analyze && (
        <div className="panel">
          <h2>Previews</h2>
          <div className="previews">
            <div>
              <div className="pre-head">Resume preview ({analyze.resume_chars} chars)</div>
              <pre>{analyze.resume_preview}</pre>
            </div>
            <div>
              <div className="pre-head">JD preview ({analyze.jd_chars} chars)</div>
              <pre>{analyze.jd_preview}</pre>
            </div>
          </div>
        </div>
      )}

      {score && (
        <div className="panel">
          <h2>Scores</h2>
          <MetricBar label="Overall" value={score.overall_score} />
          <MetricBar label="Cosine" value={score.cosine_similarity} />
          <MetricBar label="Coverage" value={score.coverage} />

          <div className="lists">
            <div>
              <div className="list-head">
                Matched ({score.matched?.length ?? 0})
                <button
                  className="mini"
                  onClick={() => navigator.clipboard.writeText((score.matched || []).join(", "))}
                >Copy</button>
              </div>
              <ul>
                {(score.matched || []).slice(0, 50).map((k) => <li key={`m-${k}`}>{k}</li>)}
              </ul>
            </div>

            <div>
              <div className="list-head">
                Missing (sample {score.missing_sample?.length ?? 0})
                <button
                  className="mini"
                  onClick={() => navigator.clipboard.writeText((score.missing_sample || []).join(", "))}
                >Copy</button>
              </div>
              <ul>
                {(score.missing_sample || []).map((k) => <li key={`x-${k}`} className="miss">{k}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
        <div>
            <button
                disabled={!canDownload}
                onClick={() => {
                    if (!downloadPayload) return;
                    const blob = new Blob([JSON.stringify(downloadPayload, null, 2)], { type: "application/json" });
                    const a = document.createElement("a");
                    a.href = URL.createObjectURL(blob);
                    a.download = score ? "resume-score.json" : "resume-analyze.json";
                    a.click();
                }} >
                Download report
            </button> 
            
    
           <button
                style={{
                    backgroundColor: resume || jd ? "#BA3D25" : "#023E8A", // orange if enabled, grey if disabled
                    color: "white",
                    cursor: resume || jd ? "pointer" : "not-allowed",
                    padding: "0.5rem 1rem ",
                    margin:10  ,
                    border: "none",
                    borderRadius: "6px"
                }}
                disabled={!resume && !jd}
                onClick={() => {
                    setResume(null);
                    setJd(null);
                    setAnalyze(null);
                    setScore(null);
                    setResetTrigger((v) => !v);
                }}
                >
                Reset
            </button>
        </div>
      

      <footer>
        API: {import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"}
      </footer>
    </div>
  );
}
