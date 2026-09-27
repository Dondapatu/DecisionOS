import { Link } from "react-router-dom";
import "../App.css";

function Home() {
  return (
    <div className="app">
      <div className="hero">
        <h1>DecisionOS</h1>

        <p>
          AI Decision Engine that reviews thousands of records before humans do.
        </p>

        <div className="buttons">
          <Link to="/upload">
            <button>Upload Documents</button>
          </Link>

          <Link to="/dashboard">
            <button className="secondary">View Dashboard</button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;