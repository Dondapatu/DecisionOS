import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import JobWorkspace from "./pages/JobWorkspace";
import Candidate from "./pages/Candidate";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/job/:id" element={<JobWorkspace />} />
        <Route path="/candidate/:id" element={<Candidate />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;