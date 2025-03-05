import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <h1>Marvel Rivals Analytics Dashboard</h1>
      <div className="dashboard-cards">
        <Link to="/heroes" className="dashboard-card">
          <h2>Hero Analytics</h2>
          <p>View statistics and performance metrics for all heroes</p>
        </Link>
        <Link to="/team-builder" className="dashboard-card">
          <h2>Team Builder</h2>
          <p>Create team compositions and get win predictions</p>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard; 