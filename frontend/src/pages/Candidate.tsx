import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import API_BASE_URL from "../config";
import "../App.css";

interface CandidateData {
  id: number;
  filename: string;
  status: string;
  score: number | null;

  name: string | null;
  email: string | null;
  phone: string | null;

  skills: string | null;
  experience: string | null;
  education: string | null;
  projects: string | null;

  skill_coverage: number | null;
  semantic_relevance: number | null;
  ai_recommendation: string | null;

  matched_skills: string | null;
  missing_skills: string | null;

  processing_stage: string | null;
  validation_status: string | null;
}

function Candidate() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [candidate, setCandidate] = useState<CandidateData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/resume/${id}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Candidate not found");
        }

        return res.json();
      })
      .then((data) => {
        setCandidate(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="app">
        <div className="candidate-page">
          <h2>Loading candidate...</h2>
        </div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="app">
        <div className="candidate-page">
          <h2>Candidate not found</h2>

          <button
            className="back-button"
            onClick={() => navigate(-1)}
          >
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  const matchedSkills = candidate.matched_skills
    ? candidate.matched_skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean)
    : [];

  const missingSkills = candidate.missing_skills
    ? candidate.missing_skills
        .split(",")
        .map((skill) => skill.trim())
        .filter(Boolean)
    : [];

  return (
    <div className="app">
      <div className="candidate-page">

        {/* HEADER */}

        <div className="candidate-header">

          <div>
            <button
              className="back-button"
              onClick={() => navigate(-1)}
            >
              ← Back to Candidates
            </button>

            <h1>
              {candidate.name || candidate.filename}
            </h1>

            <p className="candidate-file">
              {candidate.filename}
            </p>
          </div>

          <span className="status-badge">
            {candidate.status}
          </span>

        </div>


        {/* AI SUMMARY */}

        <div className="candidate-score-grid">

          {/* AI SCORE */}

          <div className="score-card primary-score">
            <span>AI Score</span>

            <strong>
              {candidate.score !== null
                ? candidate.score
                : "-"}
            </strong>

            <small>
              Overall matching score
            </small>
          </div>


          {/* SKILL COVERAGE */}

          <div className="score-card">
            <span>Skill Coverage</span>

            <strong>
              {candidate.skill_coverage !== null
                ? `${candidate.skill_coverage}%`
                : "-"}
            </strong>

            <small>
              Required skills found
            </small>
          </div>


          {/* SEMANTIC RELEVANCE */}

          <div className="score-card">
            <span>Semantic Relevance</span>

            <strong>
              {candidate.semantic_relevance !== null
                ? `${candidate.semantic_relevance}%`
                : "-"}
            </strong>

            <small>
              Resume relevance
            </small>
          </div>

        </div>


        {/* AI RECOMMENDATION */}

        <div className="ai-recommendation">

          <span>
            AI Recommendation
          </span>

          <strong>
            {candidate.ai_recommendation || "Review"}
          </strong>

          <small>
            Based on the configured score threshold
          </small>

        </div>


        {/* CANDIDATE INFORMATION */}

        <div className="candidate-section">

          <div className="section-title">
            <h2>Candidate Information</h2>
          </div>

          <div className="information-grid">

            <div className="information-item">
              <span>Name</span>

              <strong>
                {candidate.name || "-"}
              </strong>
            </div>

            <div className="information-item">
              <span>Email</span>

              <strong>
                {candidate.email || "-"}
              </strong>
            </div>

            <div className="information-item">
              <span>Phone</span>

              <strong>
                {candidate.phone || "-"}
              </strong>
            </div>

            <div className="information-item">
              <span>Processing Stage</span>

              <strong>
                {candidate.processing_stage || "-"}
              </strong>
            </div>

          </div>

        </div>


        {/* SKILL ANALYSIS */}

        <div className="candidate-section">

          <div className="section-title">

            <h2>
              Skill Analysis
            </h2>

            <p>
              Skills identified from the candidate's resume.
            </p>

          </div>


          <div className="skill-analysis-grid">

            {/* MATCHED SKILLS */}

            <div className="skill-analysis-card">

              <h3>
                Matched Skills
              </h3>

              {matchedSkills.length > 0 ? (

                <div className="candidate-skill-list">

                  {matchedSkills.map((skill) => (

                    <span
                      className="candidate-skill matched"
                      key={skill}
                    >
                      ✓ {skill}
                    </span>

                  ))}

                </div>

              ) : (

                <p>
                  No matched skills found.
                </p>

              )}

            </div>


            {/* MISSING SKILLS */}

            <div className="skill-analysis-card">

              <h3>
                Missing Skills
              </h3>

              {missingSkills.length > 0 ? (

                <div className="candidate-skill-list">

                  {missingSkills.map((skill) => (

                    <span
                      className="candidate-skill missing"
                      key={skill}
                    >
                      ! {skill}
                    </span>

                  ))}

                </div>

              ) : (

                <p className="no-missing">
                  No missing required skills detected.
                </p>

              )}

            </div>

          </div>

        </div>


        {/* EXPERIENCE */}

        <div className="candidate-section">

          <div className="section-title">
            <h2>Experience</h2>
          </div>

          <div className="content-card">

            <p>
              {candidate.experience ||
                "No experience information extracted."}
            </p>

          </div>

        </div>


        {/* EDUCATION */}

        <div className="candidate-section">

          <div className="section-title">
            <h2>Education</h2>
          </div>

          <div className="content-card">

            <p>
              {candidate.education ||
                "No education information extracted."}
            </p>

          </div>

        </div>


        {/* PROJECTS */}

        <div className="candidate-section">

          <div className="section-title">
            <h2>Projects</h2>
          </div>

          <div className="content-card">

            <p>
              {candidate.projects ||
                "No project information extracted."}
            </p>

          </div>

        </div>


        {/* ORIGINAL RESUME */}

        <div className="candidate-section">

          <div className="section-title">

            <h2>
              Original Resume
            </h2>

            <p>
              Review the original document before making a decision.
            </p>

          </div>


          <div className="resume-card">

            <div>

              <strong>
                {candidate.filename}
              </strong>

              <span>
                Original uploaded document
              </span>

            </div>


            <button
              className="resume-button"
              onClick={() => {
                window.open(
                  `${API_BASE_URL}/resume/${candidate.id}/file`,
                  "_blank"
                );
              }}
            >
              View Resume
            </button>

          </div>

        </div>


        {/* HUMAN REVIEW */}

        <div className="candidate-section review-decision-section">

          <div className="section-title">

            <h2>
              Human Review
            </h2>

            <p>
              AI analysis supports the review. The final decision
              is made by the recruiter.
            </p>

          </div>


          <div className="decision-buttons">

            <button className="decision-button shortlist">
              Shortlist
            </button>

            <button className="decision-button maybe">
              Maybe
            </button>

            <button className="decision-button reject">
              Reject
            </button>

          </div>

        </div>

      </div>
    </div>
  );
}

export default Candidate;