import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API_BASE_URL from "../config";
import "../App.css";

function Upload() {
  const [jobName, setJobName] = useState("");
  const [skills, setSkills] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);

  const navigate = useNavigate();

  async function handleSubmit() {
    if (!jobName || !skills || !files || files.length === 0) {
      alert("Please fill all required fields and select at least one file.");
      return;
    }

    try {
      // Step 1: Create Job
      const jobRes = await fetch(`${API_BASE_URL}/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_name: jobName,
          skills: skills,
          job_description: jobDescription || null,
        }),
      });

      const job = await jobRes.json();

      if (!jobRes.ok) {
        alert("Job creation failed.");
        console.log(job);
        return;
      }

      // Step 2: Upload Files
      const formData = new FormData();

      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }

      const uploadRes = await fetch(
        `${API_BASE_URL}/jobs/${job.id}/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await uploadRes.json();

      if (!uploadRes.ok) {
        alert("Upload failed.");
        console.log(result);
        return;
      }

      alert(`Uploaded ${result.count} file(s) successfully!`);

      navigate(`/job/${job.id}`);
    } catch (error) {
      console.error(error);
      alert("Something went wrong.");
    }
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

        <label>
          Job Description <span style={{ color: "#8b95aa" }}>(Optional)</span>
        </label>

        <textarea
          placeholder="Describe the role, responsibilities, experience, and requirements..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
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

        <label>Upload Resumes</label>
        <input
          type="file"
          multiple
          accept=".pdf,.zip"
          onChange={(e) => setFiles(e.target.files)}
        />

        {files && (
          <p style={{ color: "#b8c0d4", marginTop: "10px" }}>
            {files.length} file(s) selected
          </p>
        )}

        <button onClick={handleSubmit}>Start Review</button>
      </div>
    </div>
  );
}

export default Upload;