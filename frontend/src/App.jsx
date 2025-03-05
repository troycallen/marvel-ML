import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HeroAnalytics from './components/HeroAnalytics';
import TeamBuilder from './components/TeamBuilder';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/heroes" element={<HeroAnalytics />} />
            <Route path="/team-builder" element={<TeamBuilder />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 