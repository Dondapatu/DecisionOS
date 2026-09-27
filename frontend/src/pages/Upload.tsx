import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

function Upload() {
  const [jobName, setJobName] = useState("");
  const [skills, setSkills] = useState("");
  const navigate = useNavigate();

  async function handleSubmit() {
    if (!jobName || !skills) {
      alert("Please fill all fields.");
      return;
    }

    const response = await fetch("http://127.0.0.1:8000/jobs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_name: jobName,
        skills: skills,
      }),
    });

    const data = await response.json();

    alert(`Job Created!\nID: ${data.id}`);

    navigate("/dashboard");
  }

  return (
    <div className="app">
      <div className="upload-box">
        <h1>Create Review Job</h1>
        <p>Upload resumes for AI review.</p>

        <label>Job Name</label>
        <input
          type="text"
          placeholder="SDE Internship 2027"
          value={jobName}
          onChange={(e) => setJobName(e.target.value)}
        />

        <label>Required Skills</label>
        <input
          type="text"
          placeholder="Python, React, SQL"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />

        <label>Upload Resume ZIP</label>
        <input type="file" accept=".zip,.pdf" />

        <button onClick={handleSubmit}>Start Review</button>
      </div>
    </div>
  );
}

export default Upload;