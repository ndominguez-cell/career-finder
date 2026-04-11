import { useState, useRef } from 'react';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [resumeProfile, setResumeProfile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [targetLocation, setTargetLocation] = useState('Remote');
  const [targetRole, setTargetRole] = useState('Software Engineer');
  const [tailoringStatus, setTailoringStatus] = useState({});
  const [tailoredResult, setTailoredResult] = useState(null);
  const [emailStatus, setEmailStatus] = useState({});
  const [emailResult, setEmailResult] = useState(null);
  const [activeJob, setActiveJob] = useState(null);

  const fileInputRef = useRef(null);

  const handleFileClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setUploadStatus('Uploading...');

      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const res = await fetch(`${API_URL}/upload_resume`, {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        setFile(selectedFile);
        setResumeProfile(data.profile);
        if (data.profile?.title) setTargetRole(data.profile.title);
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
      const url = new URL(`${API_URL}/fetch_jobs`);
      url.searchParams.set('role', targetRole);
      url.searchParams.set('location', targetLocation);

      const res = await fetch(url.toString());
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (err) {
      console.error(err);
      alert('Failed to fetch jobs. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleTailorResume = async (job) => {
    const key = job.id || job.title;
    setTailoringStatus((prev) => ({ ...prev, [key]: true }));
    try {
      const res = await fetch(`${API_URL}/tailor_resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job,
          base_resume: '', // backend uses _resume_store if empty
          openai_key: null,
        }),
      });
      const data = await res.json();
      setTailoredResult(data.tailored_resume);
    } catch (err) {
      console.error(err);
      alert('Failed to tailor resume. Is OpenAI key set?');
    } finally {
      setTailoringStatus((prev) => ({ ...prev, [key]: false }));
    }
  };

  const handleGenerateEmail = async (job) => {
    const key = job.id || job.title;
    setEmailStatus((prev) => ({ ...prev, [key]: true }));
    setActiveJob(job);
    try {
      const topQuals = resumeProfile?.skills?.slice(0, 3).join(', ') || 'Software Engineering';
      const res = await fetch(`${API_URL}/generate-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job,
          top_qualifications: topQuals,
          hiring_manager: '',
          openai_key: null,
        }),
      });
      const data = await res.json();
      setEmailResult(data.email);
    } catch (err) {
      console.error(err);
      alert('Failed to generate email. Is OpenAI key set?');
    } finally {
      setEmailStatus((prev) => ({ ...prev, [key]: false }));
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard!');
    });
  };

  return (
    <div className="container">
      <header style={{ position: 'relative' }}>
        <h1>Career Finder AI</h1>
        <p>Drop your resume, let AI score the roles, and dispatch your applications.</p>
      </header>


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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h3>Resume Loaded ✅</h3>
              <p className="text-muted" style={{ marginTop: '0.25rem' }}>
                {uploadStatus}
              </p>
              {resumeProfile && (
                <p style={{ fontSize: '0.85rem', color: 'var(--primary)', marginTop: '0.5rem' }}>
                  Detected role: <strong>{resumeProfile.title}</strong> · Skills:{' '}
                  {resumeProfile.skills?.join(', ')}
                </p>
              )}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Target Role & Location</label>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="Role (e.g. GNC Engineer)"
                  className="settings-input"
                  style={{ width: '180px', margin: 0 }}
                />
                <input
                  type="text"
                  value={targetLocation}
                  onChange={(e) => setTargetLocation(e.target.value)}
                  placeholder="Location (e.g. Remote)"
                  className="settings-input"
                  style={{ width: '150px', margin: 0 }}
                />
                <button className="btn" onClick={fetchJobs} disabled={loading}>
                  {loading ? <div className="loader"></div> : '🔍 Start Finding Jobs'}
                </button>
              </div>
            </div>
          </div>
        )}
      </section>

      {jobs.length > 0 && (
        <section className="glass-panel">
          <h2 style={{ marginBottom: '1.5rem' }}>
            Top Matches{' '}
            <span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 400 }}>
              ({jobs.length} roles scored)
            </span>
          </h2>
          <div className="jobs-list">
            {jobs.map((job, idx) => {
              const key = job.id || job.title;
              return (
                <div key={key || idx} className="job-card">
                  <div className="job-info">
                    <h3>{job.title}</h3>
                    <div>
                      <span className="job-company">{job.company}</span>
                      <span className="job-location">📍 {job.location}</span>
                    </div>
                    {job.matched_keywords?.length > 0 && (
                      <div style={{ marginTop: '0.4rem', display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                        {job.matched_keywords.slice(0, 5).map((kw) => (
                          <span key={kw} className="keyword-badge">{kw}</span>
                        ))}
                      </div>
                    )}
                    <p className="job-reasoning">"{job.reasoning}"</p>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: 'var(--primary)',
                        textDecoration: 'none',
                        fontSize: '0.8rem',
                        marginTop: '0.5rem',
                        display: 'inline-block',
                      }}
                    >
                      View Original Posting ↗
                    </a>
                  </div>

                  <div className="job-score-container">
                    <div className="job-score">{job.score}% Match</div>
                    <button
                      className="btn"
                      onClick={() => handleTailorResume(job)}
                      disabled={tailoringStatus[key]}
                      style={{ backgroundColor: 'var(--accent)' }}
                    >
                      {tailoringStatus[key] ? 'Tailoring…' : '🪄 Tailor Resume'}
                    </button>
                    <button
                      className="btn btn-success"
                      onClick={() => handleGenerateEmail(job)}
                      disabled={emailStatus[key]}
                    >
                      {emailStatus[key] ? 'Generating…' : '🚀 Generate Email'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Tailored Resume Modal */}
      {tailoredResult && (
        <div className="modal-overlay" onClick={() => setTailoredResult(null)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🪄 Tailored Resume</h2>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn" onClick={() => copyToClipboard(tailoredResult)}>
                  📋 Copy
                </button>
                <button
                  className="btn"
                  onClick={() => setTailoredResult(null)}
                  style={{ background: 'var(--danger)' }}
                >
                  Close
                </button>
              </div>
            </div>
            <pre className="result-pre">{tailoredResult}</pre>
          </div>
        </div>
      )}

      {/* Email Modal */}
      {emailResult && (
        <div className="modal-overlay" onClick={() => setEmailResult(null)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                🚀 Application Email
                {activeJob && (
                  <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 400, marginLeft: '0.5rem' }}>
                    for {activeJob.title} @ {activeJob.company}
                  </span>
                )}
              </h2>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn" onClick={() => copyToClipboard(emailResult)}>
                  📋 Copy
                </button>
                <button
                  className="btn"
                  onClick={() => setEmailResult(null)}
                  style={{ background: 'var(--danger)' }}
                >
                  Close
                </button>
              </div>
            </div>
            <pre className="result-pre">{emailResult}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
