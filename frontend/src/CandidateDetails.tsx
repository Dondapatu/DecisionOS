import { useEffect, useState } from "react";
import API_BASE_URL from "./config";
import { useNavigate, useParams } from "react-router-dom";
import "./App.css";

interface Candidate {
  id: number;
  job_id: string;
  filename: string;
  status: string;

  score: number | null;
  rank: number | null;

  name: string | null;
  email: string | null;
  phone: string | null;

  skills: string | null;
  skill_coverage: number | null;
  semantic_relevance: number | null;

  matched_skills: string | null;
  missing_skills: string | null;

  experience: string | null;
  education: string | null;
  projects: string | null;

  ai_recommendation: string | null;

  document_type: string | null;
  validation_status: string | null;
  validation_reason: string | null;
}

function CandidateDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [candidate, setCandidate] =
    useState<Candidate | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) {
      setError("Candidate ID is missing.");
      setLoading(false);
      return;
    }

    fetch(`${API_BASE_URL}/resume/${id}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Candidate not found");
        }

        return response.json();
      })
      .then((data) => {
        setCandidate(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setError("Unable to load candidate details.");
        setLoading(false);
      });
  }, [id]);

  // --------------------------------
  // LOADING
  // --------------------------------

  if (loading) {
    return (
      <div className="app">
        <div className="candidate-page">
          <h2>Loading candidate...</h2>
        </div>
      </div>
    );
  }

  // --------------------------------
  // ERROR
  // --------------------------------

  if (error || !candidate) {
    return (
      <div className="app">
        <div className="candidate-page">

          <button
            className="back-button"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>

          <div className="candidate-error">
            <h2>Candidate Not Found</h2>

            <p>
              {error || "Unable to find this candidate."}
            </p>
          </div>

        </div>
      </div>
    );
  }

  // --------------------------------
  // IMPORTANT
  // --------------------------------
  // At this point candidate is guaranteed
  // to be available.

  const currentCandidate: Candidate = candidate;

  // --------------------------------
  // SKILL HELPERS
  // --------------------------------

  const matchedSkills = currentCandidate.matched_skills
    ? currentCandidate.matched_skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean)
    : [];

  const missingSkills = currentCandidate.missing_skills
    ? currentCandidate.missing_skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean)
    : [];

  const candidateSkills = currentCandidate.skills
    ? currentCandidate.skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean)
    : [];

  // --------------------------------
  // OPEN ORIGINAL RESUME
  // --------------------------------

  function viewOriginalResume() {
    window.open(
      `${API_BASE_URL}/resume/${currentCandidate.id}/file`,
      "_blank"
    );
  }

  return (
    <div className="app">

      <div className="candidate-page">

        {/* =====================================
            TOP BAR
        ===================================== */}

        <div className="candidate-page-header">

          <button
            className="back-button"
            onClick={() => navigate(-1)}
          >
            ← Back to Review Console
          </button>

          <button
            className="view-resume-button"
            onClick={viewOriginalResume}
          >
            View Original Resume
          </button>

        </div>

        {/* =====================================
            CANDIDATE HEADER
        ===================================== */}

        <div className="candidate-profile-card">

          <div className="candidate-profile-info">

            <div className="candidate-avatar">
              {currentCandidate.name
                ? currentCandidate.name
                    .charAt(0)
                    .toUpperCase()
                : "?"}
            </div>

            <div>

              <h1>
                {currentCandidate.name ||
                  "Unknown Candidate"}
              </h1>

              <p className="candidate-filename">
                {currentCandidate.filename}
              </p>

              <div className="candidate-contact">

                {currentCandidate.email && (
                  <span>
                    ✉ {currentCandidate.email}
                  </span>
                )}

                {currentCandidate.phone && (
                  <span>
                    ☎ {currentCandidate.phone}
                  </span>
                )}

              </div>

            </div>

          </div>

          {/* AI DECISION */}

          <div className="candidate-decision">

            <span className="decision-label">
              AI Decision
            </span>

            <strong
              className={`decision-value ${
                currentCandidate.ai_recommendation
                  ? currentCandidate.ai_recommendation.toLowerCase()
                  : ""
              }`}
            >
              {currentCandidate.ai_recommendation ||
                "Processing"}
            </strong>

          </div>

        </div>

        {/* =====================================
            AI SCREENING SUMMARY
        ===================================== */}

        <div className="candidate-section">

          <div className="candidate-section-title">

            <div>

              <h2>AI Screening Summary</h2>

              <p>
                Key signals used by DecisionOS
                during screening.
              </p>

            </div>

          </div>

          <div className="ai-metrics">

            {/* AI SCORE */}

            <div className="ai-metric-card">

              <span>AI Score</span>

              <strong>
                {currentCandidate.score ?? "-"}
              </strong>

              <small>
                out of 100
              </small>

            </div>

            {/* SKILL COVERAGE */}

            <div className="ai-metric-card">

              <span>Skill Coverage</span>

              <strong>
                {currentCandidate.skill_coverage !== null
                  ? `${currentCandidate.skill_coverage}%`
                  : "-"}
              </strong>

              <small>
                required skills matched
              </small>

            </div>

            {/* SEMANTIC RELEVANCE */}

            <div className="ai-metric-card">

              <span>Semantic Relevance</span>

              <strong>
                {currentCandidate.semantic_relevance !== null
                  ? `${currentCandidate.semantic_relevance}%`
                  : "-"}
              </strong>

              <small>
                job relevance
              </small>

            </div>

          </div>

        </div>

        {/* =====================================
            SKILL ANALYSIS
        ===================================== */}

        <div className="candidate-section">

          <div className="candidate-section-title">

            <div>

              <h2>Skill Analysis</h2>

              <p>
                Skills extracted from the resume
                and compared with the job.
              </p>

            </div>

          </div>

          <div className="skill-analysis-grid">

            {/* MATCHED */}

            <div className="skill-analysis-card">

              <h3>
                Matched Skills
              </h3>

              <div className="detail-skill-list">

                {matchedSkills.length > 0 ? (

                  matchedSkills.map((skill) => (

                    <span
                      className="detail-skill matched"
                      key={skill}
                    >
                      {skill}
                    </span>

                  ))

                ) : (

                  <span className="detail-empty">
                    No matched skills
                  </span>

                )}

              </div>

            </div>

            {/* MISSING */}

            <div className="skill-analysis-card">

              <h3>
                Missing Skills
              </h3>

              <div className="detail-skill-list">

                {missingSkills.length > 0 ? (

                  missingSkills.map((skill) => (

                    <span
                      className="detail-skill missing"
                      key={skill}
                    >
                      {skill}
                    </span>

                  ))

                ) : (

                  <span className="detail-empty">
                    No missing required skills
                  </span>

                )}

              </div>

            </div>

          </div>

          {/* ALL EXTRACTED SKILLS */}

          <div className="all-skills-card">

            <h3>
              Extracted Candidate Skills
            </h3>

            <div className="detail-skill-list">

              {candidateSkills.length > 0 ? (

                candidateSkills.map((skill) => (

                  <span
                    className="detail-skill neutral"
                    key={skill}
                  >
                    {skill}
                  </span>

                ))

              ) : (

                <span className="detail-empty">
                  No skills extracted
                </span>

              )}

            </div>

          </div>

        </div>

        {/* =====================================
            EXPERIENCE
        ===================================== */}

        <div className="candidate-section">

          <div className="candidate-section-title">

            <div>
              <h2>Experience</h2>
            </div>

          </div>

          <div className="candidate-text-card">

            {currentCandidate.experience ? (

              <p>
                {currentCandidate.experience}
              </p>

            ) : (

              <span className="detail-empty">
                No experience information extracted.
              </span>

            )}

          </div>

        </div>

        {/* =====================================
            EDUCATION
        ===================================== */}

        <div className="candidate-section">

          <div className="candidate-section-title">

            <div>
              <h2>Education</h2>
            </div>

          </div>

          <div className="candidate-text-card">

            {currentCandidate.education ? (

              <p>
                {currentCandidate.education}
              </p>

            ) : (

              <span className="detail-empty">
                No education information extracted.
              </span>

            )}

          </div>

        </div>

        {/* =====================================
            PROJECTS
        ===================================== */}

        <div className="candidate-section">

          <div className="candidate-section-title">

            <div>
              <h2>Projects</h2>
            </div>

          </div>

          <div className="candidate-text-card">

            {currentCandidate.projects ? (

              <p>
                {currentCandidate.projects}
              </p>

            ) : (

              <span className="detail-empty">
                No project information extracted.
              </span>

            )}

          </div>

        </div>

        {/* =====================================
            DOCUMENT INFORMATION
        ===================================== */}

        <div className="candidate-section">

          <div className="candidate-section-title">

            <div>
              <h2>Document Information</h2>
            </div>

          </div>

          <div className="document-info-grid">

            <div>
              <span>File</span>

              <strong>
                {currentCandidate.filename}
              </strong>
            </div>

            <div>
              <span>Document Type</span>

              <strong>
                {currentCandidate.document_type || "-"}
              </strong>
            </div>

            <div>
              <span>Validation</span>

              <strong>
                {currentCandidate.validation_status || "-"}
              </strong>
            </div>

            <div>
              <span>Processing Status</span>

              <strong>
                {currentCandidate.status}
              </strong>
            </div>

          </div>

          {currentCandidate.validation_reason && (

            <div className="validation-note">

              <strong>
                Validation Note:
              </strong>{" "}

              {currentCandidate.validation_reason}

            </div>

          )}

        </div>

        {/* =====================================
            ORIGINAL RESUME
        ===================================== */}

        <div className="resume-view-card">

          <div>

            <h2>
              Original Resume
            </h2>

            <p>
              Open the original uploaded PDF
              for human audit and verification.
            </p>

          </div>

          <button
            className="view-resume-button"
            onClick={viewOriginalResume}
          >
            Open Resume PDF
          </button>

        </div>

      </div>

    </div>
  );
}

export default CandidateDetails;