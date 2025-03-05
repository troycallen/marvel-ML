import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">Marvel Rivals Analytics</Link>
      </div>
      <div className="navbar-links">
        <Link to="/heroes">Hero Analytics</Link>
        <Link to="/team-builder">Team Builder</Link>
        <Link to="/matches">Match History</Link>
      </div>
    </nav>
  );
};

export default Navbar; 