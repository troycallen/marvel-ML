import React, { useState, useEffect } from 'react';
import './HeroAnalytics.css';

const HeroAnalytics = () => {
  const [heroStats, setHeroStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('win_rate');

  useEffect(() => {
    fetchHeroStats();
  }, []);

  const fetchHeroStats = async () => {
    try {
      const response = await fetch('/api/analytics/hero-stats');
      if (!response.ok) throw new Error('Failed to fetch hero stats');
      const data = await response.json();
      setHeroStats(Object.entries(data).map(([id, stats]) => ({
        id: parseInt(id),
        ...stats
      })));
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const sortedHeroes = [...heroStats].sort((a, b) => b[sortBy] - a[sortBy]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="hero-analytics">
      <h2>Hero Analytics</h2>
      <div className="sort-controls">
        <label>Sort by: </label>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="win_rate">Win Rate</option>
          <option value="kda">KDA</option>
          <option value="games_played">Games Played</option>
          <option value="avg_damage">Average Damage</option>
        </select>
      </div>
      <div className="hero-stats-grid">
        {sortedHeroes.map(hero => (
          <div key={hero.id} className="hero-card">
            <h3>Hero {hero.id}</h3>
            <div className="stat-row">
              <span>Win Rate:</span>
              <span>{(hero.win_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="stat-row">
              <span>KDA:</span>
              <span>{hero.kda.toFixed(2)}</span>
            </div>
            <div className="stat-row">
              <span>Games:</span>
              <span>{hero.games_played}</span>
            </div>
            <div className="stat-row">
              <span>Avg Damage:</span>
              <span>{Math.round(hero.avg_damage)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HeroAnalytics; 