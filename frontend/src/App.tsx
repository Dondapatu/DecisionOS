import "./App.css";

function App() {
  return (
    <div className="app">
      <div className="hero">
        <h1>DecisionOS</h1>

        <p>
          AI Decision Engine that reviews thousands of records before humans do.
        </p>

        <div className="buttons">
          <button>Upload Documents</button>
          <button className="secondary">View Dashboard</button>
        </div>
      </div>
    </div>
  );
}

export default App;