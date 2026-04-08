import { useState, useRef } from 'react';
import './index.css';

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchApiKey, setSearchApiKey] = useState('');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [tailoringStatus, setTailoringStatus] = useState({});
  const [tailoredResult, setTailoredResult] = useState(null);
  
  const fileInputRef = useRef(null);

  const handleFileClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setUploadStatus('Uploading...');
      
      const formData = new FormData();
      formData.append("file", selectedFile);

      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/upload_resume`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        setUploadStatus(`Processed: ${data.filename}`);
      } catch (err) {
        setUploadStatus('Error uploading resume');
        console.error(err);
      }
    }
  };

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const headers = {};
      if (searchApiKey) {
        headers["X-Searchapi-Key"] = searchApiKey;
      }
      
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/fetch_jobs`, {
        headers
      });
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch jobs. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleTailorResume = async (job) => {
    setTailoringStatus(prev => ({ ...prev, [job.title]: true }));
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/tailor_resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job: job, base_resume: "Candidate Base Resume", openai_key: openaiApiKey })
      });
      const data = await res.json();
      setTailoredResult(data.tailored_resume);
    } catch (err) {
      console.error(err);
      alert("Failed to tailor resume");
    } finally {
      setTailoringStatus(prev => ({ ...prev, [job.title]: false }));
    }
  };

  return (
    <div className="container">
      <header style={{ position: 'relative' }}>
        <h1>Career Finder AI</h1>
        <p>Drop your resume, let AI score the roles, and dispatch your applications.</p>
        
        <button 
          onClick={() => setShowConfig(!showConfig)} 
          className="btn" 
          style={{ position: 'absolute', top: '10px', right: '10px', padding: '0.4rem 0.8rem', fontSize: '0.9rem', backgroundColor: 'var(--glass-bg)', color: 'var(--text)' }}
        >
          ⚙️ Settings
        </button>
      </header>

      {showConfig && (
        <section className="glass-panel" style={{ marginBottom: '1.5rem', padding: '1.5rem', border: '1px solid var(--primary)' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            User Configuration
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>SearchApi.io Key (Optional, bypasses .env)</label>
            <input 
              type="password" 
              value={searchApiKey}
              onChange={(e) => setSearchApiKey(e.target.value)}
              placeholder="Paste your key here..."
              style={{
                width: '100%',
                padding: '0.8rem',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(0,0,0,0.2)',
                color: 'white',
                fontSize: '1rem',
                fontFamily: 'inherit'
              }}
            />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Used by the AI background agent to bypass LinkedIn/Indeed captchas via SearchApi.</p>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1rem' }}>
            <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>OpenAI API Key (Optional, bypasses .env)</label>
            <input 
              type="password" 
              value={openaiApiKey}
              onChange={(e) => setOpenaiApiKey(e.target.value)}
              placeholder="sk-proj-..."
              style={{
                width: '100%',
                padding: '0.8rem',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(0,0,0,0.2)',
                color: 'white',
                fontSize: '1rem',
                fontFamily: 'inherit'
              }}
            />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Used to bypass the ATS matching engine and rewrite your resume dynamically.</p>
          </div>
        </section>
      )}

      <section className="glass-panel">
        {!file ? (
          <div className="upload-area" onClick={handleFileClick}>
            <div className="upload-icon">📄</div>
            <h2>Upload Resume</h2>
            <p className="text-muted">PDF or Word Document</p>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx"
            />
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3>Resume Loaded ✅</h3>
              <p className="text-muted" style={{marginTop: '0.25rem'}}>{uploadStatus}</p>
            </div>
            <button className="btn" onClick={fetchJobs} disabled={loading}>
              {loading ? <div className="loader"></div> : '🔍 Start Finding Jobs'}
            </button>
          </div>
        )}
      </section>

      {jobs.length > 0 && (
        <section className="glass-panel">
          <h2 style={{ marginBottom: '1.5rem' }}>Top Matches</h2>
          <div className="jobs-list">
            {jobs.map((job, idx) => (
              <div key={job.id || idx} className="job-card">
                <div className="job-info">
                  <h3>{job.title}</h3>
                  <div>
                    <span className="job-company">{job.company}</span>
                    <span className="job-location">📍 {job.location}</span>
                  </div>
                  <p className="job-reasoning">"{job.reasoning}"</p>
                  <a href={job.url} target="_blank" rel="noopener noreferrer" style={{color: 'var(--primary)', textDecoration: 'none', fontSize: '0.8rem', marginTop: '0.5rem', display: 'inline-block'}}>
                    View Original Posting ↗
                  </a>
                </div>
                
                <div className="job-score-container" style={{display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end'}}>
                  <div className="job-score">{job.score}% Match</div>
                  <button 
                    className="btn" 
                    onClick={() => handleTailorResume(job)}
                    disabled={tailoringStatus[job.title]}
                    style={{backgroundColor: 'var(--accent)'}}
                  >
                    {tailoringStatus[job.title] ? 'Tailoring...' : '🪄 Tailor Resume'}
                  </button>
                  <button className="btn btn-success" onClick={() => alert(`Send pipeline triggered for ${job.title} at ${job.company}!`)}>
                    🚀 Send Application
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {tailoredResult && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 1000,
          display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '2rem'
        }}>
          <div className="glass-panel" style={{width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
              <h2>Tailored Resume Result</h2>
              <button className="btn" onClick={() => setTailoredResult(null)} style={{background: 'var(--danger)'}}>Close</button>
            </div>
            <pre style={{whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.9rem', color: '#e2e8f0', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px'}}>
              {tailoredResult}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
