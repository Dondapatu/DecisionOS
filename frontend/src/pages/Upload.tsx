import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

function Upload() {
  const [jobName, setJobName] = useState("");
  const [skills, setSkills] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);

  const navigate = useNavigate();

  async function handleSubmit() {
    if (!jobName || !skills || !files || files.length === 0) {
      alert("Please fill all fields and select at least one file.");
      return;
    }

    try {
      // Step 1: Create Job
      const jobRes = await fetch("http://127.0.0.1:8000/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_name: jobName,
          skills: skills,
        }),
      });

      const job = await jobRes.json();

      // Step 2: Upload Files
      const formData = new FormData();

      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }

      const uploadRes = await fetch(
        `http://127.0.0.1:8000/jobs/${job.id}/upload`,
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