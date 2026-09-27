import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

interface Job {
  id: string;
  job_name: string;
  skills: string;
  status: string;
}

function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8000/jobs")
      .then((res) => res.json())
      .then((data) => setJobs(data))
      .catch((err) => console.error("Error fetching jobs:", err));
  }, []);

  return (
    <div className="app">
      <div className="dashboard">
        <h1>DecisionOS Dashboard</h1>

        <div className="cards">
          <div className="card">
            <h2>{jobs.length}</h2>
            <p>Total Jobs</p>
          </div>

          <div className="card">
            <h2>{jobs.filter((j) => j.status === "Created").length}</h2>
            <p>Created</p>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Job Name</th>
              <th>Skills</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {jobs.map((job) => (
              <tr
                key={job.id}
                onClick={() => navigate(`/job/${job.id}`)}
                style={{ cursor: "pointer" }}
              >
                <td>{job.id}</td>
                <td>{job.job_name}</td>
                <td>{job.skills}</td>
                <td>{job.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;