import React, { useState, useEffect } from 'react';
import './TeamBuilder.css';

const TeamBuilder = () => {
  const [heroes, setHeroes] = useState([]);
  const [team1, setTeam1] = useState([]);
  const [team2, setTeam2] = useState([]);
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    fetchHeroes();
  }, []);

  const fetchHeroes = async () => {
    try {
      const response = await fetch('/api/heroes');
      if (!response.ok) throw new Error('Failed to fetch heroes');
      const data = await response.json();
      setHeroes(data);
    } catch (error) {
      console.error('Error fetching heroes:', error);
    }
  };

  const addToTeam = (hero, team) => {
    if (team === 1 && team1.length < 3) {
      setTeam1([...team1, hero]);
    } else if (team === 2 && team2.length < 3) {
      setTeam2([...team2, hero]);
    }
  };

  const removeFromTeam = (heroId, team) => {
    if (team === 1) {
      setTeam1(team1.filter(h => h.id !== heroId));
    } else {
      setTeam2(team2.filter(h => h.id !== heroId));
    }
  };

  const getPrediction = async () => {
    if (team1.length === 3 && team2.length === 3) {
      try {
        const response = await fetch('/api/predictions/match-outcome', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            team1: team1.map(h => h.id),
            team2: team2.map(h => h.id)
          })
        });
        const data = await response.json();
        setPrediction(data);
      } catch (error) {
        console.error('Error getting prediction:', error);
      }
    }
  };

  return (
    <div className="team-builder">
      <div className="teams-container">
        <div className="team">
          <h3>Team 1</h3>
          <div className="team-heroes">
            {team1.map(hero => (
              <div key={hero.id} className="selected-hero" 
                   onClick={() => removeFromTeam(hero.id, 1)}>
                Hero {hero.id}
              </div>
            ))}
          </div>
        </div>
        
        <div className="team">
          <h3>Team 2</h3>
          <div className="team-heroes">
            {team2.map(hero => (
              <div key={hero.id} className="selected-hero"
                   onClick={() => removeFromTeam(hero.id, 2)}>
                Hero {hero.id}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="hero-selection">
        <h3>Available Heroes</h3>
        <div className="heroes-grid">
          {heroes.map(hero => (
            <div key={hero.id} className="hero-option"
                 onClick={() => {
                   if (!team1.includes(hero) && !team2.includes(hero)) {
                     addToTeam(hero, team1.length < 3 ? 1 : 2);
                   }
                 }}>
              Hero {hero.id}
            </div>
          ))}
        </div>
      </div>

      {team1.length === 3 && team2.length === 3 && (
        <button className="predict-button" onClick={getPrediction}>
          Predict Winner
        </button>
      )}

      {prediction && (
        <div className="prediction-result">
          <h3>Prediction</h3>
          <p>Team {prediction.predicted_winner} is likely to win!</p>
          <p>Win Probability: {(prediction.win_probability * 100).toFixed(1)}%</p>
        </div>
      )}
    </div>
  );
};

export default TeamBuilder; 