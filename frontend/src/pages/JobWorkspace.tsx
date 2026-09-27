import { useParams } from "react-router-dom";
import "../App.css";

function JobWorkspace() {
  const { id } = useParams();

  return (
    <div className="app">
      <div className="workspace">
        <h1>Job Workspace</h1>

        <p>Job ID: {id}</p>

        <div className="cards">
          <div className="card">
            <h2>0</h2>
            <p>Resumes</p>
          </div>

          <div className="card">
            <h2>Created</h2>
            <p>Status</p>
          </div>

          <div className="card">
            <h2>0</h2>
            <p>AI Reviewed</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default JobWorkspace;