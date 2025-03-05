import React, { useState, useEffect } from 'react';
import * as d3 from 'd3';

const Dashboard = () => {
  const [matchData, setMatchData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatchData();
  }, []);

  const fetchMatchData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/matches/recent');
      const data = await response.json();
      setMatchData(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching match data:', error);
      setLoading(false);
    }
  };

  const renderWinRateChart = () => {
    // D3.js visualization code here
    const svg = d3.select('#win-rate-chart');
    // ... implement win rate visualization
  };

  return (
    <div className="dashboard">
      <h1>Marvel Rivals Analytics Dashboard</h1>
      
      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Matches</h3>
              <p>{matchData.total_matches}</p>
            </div>
            <div className="stat-card">
              <h3>Average Win Rate</h3>
              <p>{matchData.avg_win_rate}%</p>
            </div>
          </div>
          
          <div className="chart-container">
            <h2>Win Rates by Team Composition</h2>
            <div id="win-rate-chart"></div>
          </div>
          
          <div className="recommendations">
            <h2>Recommended Team Compositions</h2>
            {/* Display Nash equilibrium results */}
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard; 