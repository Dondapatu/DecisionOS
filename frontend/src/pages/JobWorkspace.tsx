import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "../App.css";

interface Job {
  id: string;
  job_name: string;
  skills: string;
  job_description: string | null;
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
  ai_recommendation: string | null;
}

function JobWorkspace() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [job, setJob] = useState<Job | null>(null);
  const [resumes, setResumes] = useState<Resume[]>([]);

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const [editingJob, setEditingJob] = useState(false);
  const [savingJob, setSavingJob] = useState(false);

  const [editJobName, setEditJobName] = useState("");
  const [editSkills, setEditSkills] = useState("");
  const [editJobDescription, setEditJobDescription] = useState("");

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // --------------------------------
  // LOAD JOB + RESUMES
  // --------------------------------

  useEffect(() => {
    function loadData() {
      if (!id) {
        return;
      }

      fetch(`http://127.0.0.1:8000/jobs/${id}`)
        .then((res) => res.json())
        .then((data) => setJob(data))
        .catch((error) => {
          console.error("Failed to load job:", error);
        });

      fetch(`http://127.0.0.1:8000/jobs/${id}/resumes`)
        .then((res) => res.json())
        .then((data) => setResumes(data))
        .catch((error) => {
          console.error("Failed to load resumes:", error);
        });
    }

    loadData();

    const interval = setInterval(loadData, 2000);

    return () => clearInterval(interval);
  }, [id]);

  // --------------------------------
  // START EDITING JOB
  // --------------------------------

  function startEditingJob() {
    if (!job) {
      return;
    }

    setEditJobName(job.job_name);
    setEditSkills(job.skills);
    setEditJobDescription(job.job_description || "");

    setEditingJob(true);
    setUploadMessage("");
  }

  // --------------------------------
  // CANCEL EDITING
  // --------------------------------

  function cancelEditingJob() {
    setEditingJob(false);
  }

  // --------------------------------
  // SAVE JOB
  // --------------------------------

  async function saveJob() {
    if (!id) {
      return;
    }

    if (!editJobName.trim() || !editSkills.trim()) {
      alert("Job Name and Required Skills are required.");
      return;
    }

    setSavingJob(true);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/jobs/${id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            job_name: editJobName.trim(),
            skills: editSkills.trim(),
            job_description:
              editJobDescription.trim() || null,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        console.error(data);
        alert("Failed to update job.");
        return;
      }

      setJob(data);
      setEditingJob(false);

      setUploadMessage(
        "Job details updated successfully."
      );
    } catch (error) {
      console.error(error);
      alert("Something went wrong while updating the job.");
    } finally {
      setSavingJob(false);
    }
  }

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

  // --------------------------------
  // LOADING
  // --------------------------------

  if (!job) {
    return (
      <div className="app">
        <h2>Loading...</h2>
      </div>
    );
  }

  // --------------------------------
  // RESUME GROUPS
  // --------------------------------

  const scoredResumes = resumes.filter(
    (resume) => resume.score !== null
  );

  const processingResumes = resumes.filter(
    (resume) =>
      resume.score === null &&
      resume.status !== "Excluded"
  );

  const shortlistResumes = scoredResumes.filter(
    (resume) => resume.ai_recommendation === "Shortlist"
  );

  const reviewResumes = scoredResumes.filter(
    (resume) => resume.ai_recommendation === "Review"
  );

  const rejectResumes = scoredResumes.filter(
    (resume) => resume.ai_recommendation === "Reject"
  );

  // --------------------------------
  // VIEW CANDIDATE
  // --------------------------------

  function viewCandidate(resumeId: number) {
    navigate(`/candidate/${resumeId}`);
  }

  return (
    <div className="app">
      <div className="workspace">

        {/* ========================================
            HEADER
        ======================================== */}

        <div className="workspace-header">

          <div>
            <h1>{job.job_name}</h1>
            <p>Job ID: {job.id}</p>
          </div>

          <div className="workspace-actions">

            {/* EDIT JOB */}

            <button
              className="back-button"
              onClick={startEditingJob}
              disabled={editingJob}
            >
              Edit Job
            </button>

            {/* ADD RESUMES */}

            <button
              className="add-resumes-button"
              onClick={() =>
                fileInputRef.current?.click()
              }
              disabled={uploading || editingJob}
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

        {/* ========================================
            EDIT JOB PANEL
        ======================================== */}

        {editingJob && (
          <div className="upload-panel">

            <div style={{ width: "100%" }}>

              <h3>Edit Job</h3>

              <p>
                Update the job information used by DecisionOS.
              </p>

              <label>Job Name</label>

              <input
                type="text"
                value={editJobName}
                onChange={(e) =>
                  setEditJobName(e.target.value)
                }
                placeholder="Python Developer"
              />

              <label>Required Skills</label>

              <input
                type="text"
                value={editSkills}
                onChange={(e) =>
                  setEditSkills(e.target.value)
                }
                placeholder="Python, SQL, FastAPI"
              />

              <label>
                Job Description{" "}
                <span style={{ color: "#8b95aa" }}>
                  (Optional)
                </span>
              </label>

              <textarea
                value={editJobDescription}
                onChange={(e) =>
                  setEditJobDescription(e.target.value)
                }
                placeholder="Describe the role, responsibilities, experience, and requirements..."
                rows={6}
                style={{
                  width: "100%",
                  boxSizing: "border-box",
                  resize: "vertical",
                  padding: "12px",
                  borderRadius: "8px",
                  border: "1px solid #dbe3ef",
                  fontFamily: "inherit",
                  fontSize: "14px",
                }}
              />

              <div
                style={{
                  display: "flex",
                  gap: "10px",
                  marginTop: "15px",
                }}
              >

                <button
                  className="upload-resumes-button"
                  onClick={saveJob}
                  disabled={savingJob}
                >
                  {savingJob
                    ? "Saving..."
                    : "Save Changes"}
                </button>

                <button
                  className="back-button"
                  onClick={cancelEditingJob}
                  disabled={savingJob}
                >
                  Cancel
                </button>

              </div>

            </div>

          </div>
        )}

        {/* ========================================
            ADD RESUMES PANEL
        ======================================== */}

        {selectedFiles.length > 0 && !editingJob && (
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

        {/* ========================================
            UPLOAD MESSAGE
        ======================================== */}

        {uploadMessage && (
          <div className="upload-message">
            {uploadMessage}
          </div>
        )}

        {/* ========================================
            SUMMARY CARDS
        ======================================== */}

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

        {/* ========================================
            JOB REQUIREMENTS
        ======================================== */}

        <div className="job-requirements">

          <h2>Required Skills</h2>

          <p>{job.skills}</p>

          {job.job_description && (
            <>
              <h2>Job Description</h2>

              <p>{job.job_description}</p>
            </>
          )}

        </div>

        {/* ========================================
            CANDIDATE REVIEW CONSOLE
        ======================================== */}

        <div className="review-section">

          <div className="section-header">

            <div>

              <h2>Candidate Review Console</h2>

              <p>
                AI automatically classifies candidates
                based on their screening score.
              </p>

            </div>

            <span className="candidate-count">
              {scoredResumes.length} Scored Candidates
            </span>

          </div>

          {/* ======================================
              NO RESUMES
          ====================================== */}

          {resumes.length === 0 ? (

            <div className="empty-state">

              <h3>No resumes uploaded</h3>

              <p>
                Click "+ Add Resumes" to upload resumes
                for this job.
              </p>

            </div>

          ) : (

            <>

              {/* ==================================
                  SHORTLIST
              ================================== */}

              <div className="console-group">

                <div className="console-group-header">

                  <div>

                    <h3>Shortlist</h3>

                    <p>
                      AI score: 61–100
                    </p>

                  </div>

                  <span className="console-count">
                    {shortlistResumes.length}
                  </span>

                </div>

                <div className="table-container">

                  <table className="candidate-table">

                    <thead>

                      <tr>

                        <th>Rank</th>
                        <th>Candidate</th>
                        <th>AI Score</th>
                        <th>Skills</th>
                        <th>Status</th>
                        <th>Action</th>

                      </tr>

                    </thead>

                    <tbody>

                      {shortlistResumes.map(
                        (resume) => (

                          <tr key={resume.id}>

                            <td>

                              {resume.rank ? (

                                <span className="rank-badge">
                                  #{resume.rank}
                                </span>

                              ) : (
                                "-"
                              )}

                            </td>

                            <td>

                              <div className="candidate-info">

                                <strong>
                                  {resume.name ||
                                    "Unknown Candidate"}
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

                            <td>

                              <span className="score-value">
                                {resume.score}
                              </span>

                            </td>

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

                            <td>

                              <span className="status-badge">
                                {resume.ai_recommendation}
                              </span>

                            </td>

                            <td>

                              <button
                                className="view-candidate-button"
                                onClick={() =>
                                  viewCandidate(resume.id)
                                }
                              >
                                View Details
                              </button>

                            </td>

                          </tr>

                        )
                      )}

                      {shortlistResumes.length === 0 && (

                        <tr>

                          <td colSpan={6}>
                            No shortlisted candidates yet.
                          </td>

                        </tr>

                      )}

                    </tbody>

                  </table>

                </div>

              </div>

              {/* ==================================
                  REVIEW
              ================================== */}

              <div className="console-group">

                <div className="console-group-header">

                  <div>

                    <h3>Review</h3>

                    <p>
                      AI score: 50–60
                    </p>

                  </div>

                  <span className="console-count">
                    {reviewResumes.length}
                  </span>

                </div>

                <div className="table-container">

                  <table className="candidate-table">

                    <thead>

                      <tr>

                        <th>Rank</th>
                        <th>Candidate</th>
                        <th>AI Score</th>
                        <th>Skills</th>
                        <th>Status</th>
                        <th>Action</th>

                      </tr>

                    </thead>

                    <tbody>

                      {reviewResumes.map(
                        (resume) => (

                          <tr key={resume.id}>

                            <td>

                              {resume.rank ? (

                                <span className="rank-badge">
                                  #{resume.rank}
                                </span>

                              ) : (
                                "-"
                              )}

                            </td>

                            <td>

                              <div className="candidate-info">

                                <strong>
                                  {resume.name ||
                                    "Unknown Candidate"}
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

                            <td>

                              <span className="score-value">
                                {resume.score}
                              </span>

                            </td>

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

                            <td>

                              <span className="status-badge">
                                {resume.ai_recommendation}
                              </span>

                            </td>

                            <td>

                              <button
                                className="view-candidate-button"
                                onClick={() =>
                                  viewCandidate(resume.id)
                                }
                              >
                                View Details
                              </button>

                            </td>

                          </tr>

                        )
                      )}

                      {reviewResumes.length === 0 && (

                        <tr>

                          <td colSpan={6}>
                            No candidates currently require review.
                          </td>

                        </tr>

                      )}

                    </tbody>

                  </table>

                </div>

              </div>

              {/* ==================================
                  REJECT
              ================================== */}

              <div className="console-group">

                <div className="console-group-header">

                  <div>

                    <h3>Reject</h3>

                    <p>
                      AI score: 0–49
                    </p>

                  </div>

                  <span className="console-count">
                    {rejectResumes.length}
                  </span>

                </div>

                <div className="table-container">

                  <table className="candidate-table">

                    <thead>

                      <tr>

                        <th>Candidate</th>
                        <th>AI Score</th>
                        <th>Missing Skills</th>
                        <th>Status</th>
                        <th>Action</th>

                      </tr>

                    </thead>

                    <tbody>

                      {rejectResumes.map(
                        (resume) => (

                          <tr key={resume.id}>

                            <td>

                              <div className="candidate-info">

                                <strong>
                                  {resume.name ||
                                    "Unknown Candidate"}
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

                            <td>

                              <span className="score-value">
                                {resume.score}
                              </span>

                            </td>

                            <td>

                              <div className="skill-list">

                                {resume.missing_skills
                                  ? resume.missing_skills
                                      .split(",")
                                      .map((skill) => (

                                        <span
                                          className="skill-tag missing"
                                          key={skill}
                                        >
                                          {skill.trim()}
                                        </span>

                                      ))
                                  : (

                                    <span className="no-missing">
                                      None
                                    </span>

                                  )}

                              </div>

                            </td>

                            <td>

                              <span className="status-badge">
                                {resume.ai_recommendation}
                              </span>

                            </td>

                            <td>

                              <button
                                className="view-candidate-button"
                                onClick={() =>
                                  viewCandidate(resume.id)
                                }
                              >
                                View Details
                              </button>

                            </td>

                          </tr>

                        )
                      )}

                      {rejectResumes.length === 0 && (

                        <tr>

                          <td colSpan={5}>
                            No rejected candidates.
                          </td>

                        </tr>

                      )}

                    </tbody>

                  </table>

                </div>

              </div>

            </>

          )}

        </div>

      </div>
    </div>
  );
}

export default JobWorkspace;