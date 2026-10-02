import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../App.css";

interface Job {
  id: string;
  job_name: string;
  skills: string;
  status: string;
}

interface Resume {
  id: number;
  filename: string;
  status: string;
  score: number | null;
  rank: number | null;
  name: string | null;
  email: string | null;
  phone: string | null;
  skill_coverage: number | null;
  semantic_relevance: number | null;
  matched_skills: string | null;
  missing_skills: string | null;
}

function JobWorkspace() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    function loadData() {
      fetch(`http://127.0.0.1:8000/jobs/${id}`)
        .then((res) => res.json())
        .then((data) => setJob(data));

      fetch(`http://127.0.0.1:8000/jobs/${id}/resumes`)
        .then((res) => res.json())
        .then((data) => setResumes(data));
    }

    loadData();

    const interval = setInterval(loadData, 2000);

    return () => clearInterval(interval);
  }, [id]);

  // --------------------------------
  // SELECT RESUMES
  // --------------------------------
  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    if (!event.target.files) {
      return;
    }

    const files = Array.from(event.target.files);

    setSelectedFiles(files);
    setUploadMessage("");
  }

  // --------------------------------
  // UPLOAD RESUMES
  // --------------------------------
  async function uploadResumes() {
    if (!id) {
      return;
    }

    if (selectedFiles.length === 0) {
      setUploadMessage("Please select at least one resume.");
      return;
    }

    setUploading(true);
    setUploadMessage("");

    try {
      const formData = new FormData();

      selectedFiles.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(
        `http://127.0.0.1:8000/jobs/${id}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      setUploadMessage(
        `${data.count} resume(s) uploaded successfully. AI processing started.`
      );

      setSelectedFiles([]);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error(error);

      setUploadMessage(
        "Upload failed. Please check the backend."
      );
    } finally {
      setUploading(false);
    }
  }

  if (!job) {
    return (
      <div className="app">
        <h2>Loading...</h2>
      </div>
    );
  }

  const scoredResumes = resumes.filter(
    (resume) => resume.score !== null
  );

  const processingResumes = resumes.filter(
    (resume) => resume.score === null
  );

  return (
    <div className="app">
      <div className="workspace">

        {/* HEADER */}
        <div className="workspace-header">

          <div>
            <h1>{job.job_name}</h1>
            <p>Job ID: {job.id}</p>
          </div>

          <div className="workspace-actions">

            {/* ADD RESUMES */}
            <button
              className="add-resumes-button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploading}
            >
              + Add Resumes
            </button>

            {/* HIDDEN FILE INPUT */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
              onChange={handleFileChange}
              style={{ display: "none" }}
            />

            {/* DASHBOARD */}
            <button
              className="back-button"
              onClick={() => navigate("/dashboard")}
            >
              ← Dashboard
            </button>

          </div>

        </div>

        {/* ADD RESUMES PANEL */}
        {selectedFiles.length > 0 && (
          <div className="upload-panel">

            <div>
              <h3>
                {selectedFiles.length} resume(s) selected
              </h3>

              <p>
                These resumes will be added to this existing job
                and automatically processed by AI.
              </p>
            </div>

            <button
              className="upload-resumes-button"
              onClick={uploadResumes}
              disabled={uploading}
            >
              {uploading
                ? "Uploading..."
                : "Upload & Start AI Screening"}
            </button>

          </div>
        )}

        {/* UPLOAD MESSAGE */}
        {uploadMessage && (
          <div className="upload-message">
            {uploadMessage}
          </div>
        )}

        {/* SUMMARY CARDS */}
        <div className="cards">

          <div className="card">
            <h2>{job.status}</h2>
            <p>Job Status</p>
          </div>

          <div className="card">
            <h2>{resumes.length}</h2>
            <p>Total Resumes</p>
          </div>

          <div className="card">
            <h2>{scoredResumes.length}</h2>
            <p>Scored</p>
          </div>

          <div className="card">
            <h2>{processingResumes.length}</h2>
            <p>Processing</p>
          </div>

        </div>

        {/* REQUIRED SKILLS */}
        <div className="job-requirements">
          <h2>Required Skills</h2>
          <p>{job.skills}</p>
        </div>

        {/* REVIEW CONSOLE */}
        <div className="review-section">

          <div className="section-header">

            <div>
              <h2>Candidate Review Console</h2>

              <p>
                Candidates are ordered by AI score for human review.
              </p>
            </div>

            <span className="candidate-count">
              {scoredResumes.length} Scored Candidates
            </span>

          </div>

          {resumes.length === 0 ? (

            <div className="empty-state">

              <h3>No resumes uploaded</h3>

              <p>
                Click "+ Add Resumes" to upload resumes
                for this job.
              </p>

            </div>

          ) : (

            <div className="table-container">

              <table className="candidate-table">

                <thead>

                  <tr>
                    <th>Rank</th>
                    <th>Candidate</th>
                    <th>AI Score</th>
                    <th>Skill Coverage</th>
                    <th>Matched Skills</th>
                    <th>Missing Skills</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>

                </thead>

                <tbody>

                  {resumes.map((resume) => (

                    <tr key={resume.id}>

                      {/* RANK */}
                      <td>
                        {resume.rank ? (
                          <span className="rank-badge">
                            #{resume.rank}
                          </span>
                        ) : (
                          "-"
                        )}
                      </td>

                      {/* CANDIDATE */}
                      <td>

                        <div className="candidate-info">

                          <strong>
                            {resume.name || "Processing..."}
                          </strong>

                          <span>
                            {resume.filename}
                          </span>

                          {resume.email && (
                            <small>
                              {resume.email}
                            </small>
                          )}

                        </div>

                      </td>

                      {/* SCORE */}
                      <td>

                        {resume.score !== null ? (

                          <span className="score-value">
                            {resume.score}
                          </span>

                        ) : (

                          <span className="processing">
                            Processing
                          </span>

                        )}

                      </td>

                      {/* SKILL COVERAGE */}
                      <td>

                        {resume.skill_coverage !== null
                          ? `${resume.skill_coverage}%`
                          : "-"}

                      </td>

                      {/* MATCHED SKILLS */}
                      <td>

                        <div className="skill-list">

                          {resume.matched_skills
                            ? resume.matched_skills
                                .split(",")
                                .map((skill) => (

                                  <span
                                    className="skill-tag matched"
                                    key={skill}
                                  >
                                    {skill.trim()}
                                  </span>

                                ))
                            : "-"}

                        </div>

                      </td>

                      {/* MISSING SKILLS */}
                      <td>

                        <div className="skill-list">

                          {resume.missing_skills ? (

                            resume.missing_skills
                              .split(",")
                              .map((skill) => (

                                <span
                                  className="skill-tag missing"
                                  key={skill}
                                >
                                  {skill.trim()}
                                </span>

                              ))

                          ) : (

                            <span className="no-missing">
                              None
                            </span>

                          )}

                        </div>

                      </td>

                      {/* STATUS */}
                      <td>

                        <span className="status-badge">
                          {resume.status}
                        </span>

                      </td>

                      {/* ACTION */}
                      <td>

                        <button
                          className="review-button"
                          onClick={() =>
                            navigate(
                              `/candidate/${resume.id}`
                            )
                          }
                        >
                          Review
                        </button>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>
    </div>
  );
}

export default JobWorkspace;