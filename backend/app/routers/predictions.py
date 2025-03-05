from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db, redis_client
import json
from app import models
from app.analysis.nash_equilibrium import TeamCompositionAnalyzer
from app.analysis.game_tree import GameTreeAnalysis
from pydantic import BaseModel

router = APIRouter()

class TeamPredictionRequest(BaseModel):
    team1: List[int]  # List of hero IDs
    team2: List[int]  # List of hero IDs

class TeamPredictionResponse(BaseModel):
    win_probability: float
    confidence: float
    key_matchups: List[Dict[str, any]]

class CounterTeamRequest(BaseModel):
    enemy_team: List[int]  # List of hero IDs
    available_heroes: Optional[List[int]] = None  # Optional list of available hero IDs

class CounterTeamResponse(BaseModel):
    recommended_team: List[int]
    win_probability: float
    hero_explanations: List[Dict[str, any]]

@router.post("/match-outcome", response_model=TeamPredictionResponse)
def predict_match_outcome(
    request: TeamPredictionRequest,
    db: Session = Depends(get_db)
):
    # Validate hero IDs
    all_heroes = set(h.id for h in db.query(models.Hero).all())
    for hero_id in request.team1 + request.team2:
        if hero_id not in all_heroes:
            raise HTTPException(status_code=400, detail=f"Invalid hero ID: {hero_id}")
    
    # Try to get from cache
    cache_key = f"prediction:{','.join(map(str, sorted(request.team1)))}:{','.join(map(str, sorted(request.team2)))}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Get all matches for analysis
    matches = db.query(models.Match).all()
    match_heroes = db.query(models.MatchHero).all()
    
    # Format match data for analysis
    match_data = []
    for match in matches:
        heroes = [
            {
                "hero_id": mh.hero_id,
                "team": mh.team
            }
            for mh in match_heroes if mh.match_id == match.id
        ]
        
        match_data.append({
            "id": match.id,
            "winner_team": match.winner_team,
            "heroes": heroes
        })
    
    # Get hero data
    heroes = db.query(models.Hero).all()
    hero_pool = [{"id": h.id, "name": h.name} for h in heroes]
    
    # Initialize game tree analysis
    game_tree = GameTreeAnalysis(hero_pool)
    game_tree.initialize_matchup_matrix(match_data)
    
    # Predict outcome
    win_probability = game_tree.predict_matchup(request.team1, request.team2)
    
    # Identify key matchups
    key_matchups = []
    for hero1 in request.team1:
        for hero2 in request.team2:
            hero1_idx = next(i for i, h in enumerate(hero_pool) if h["id"] == hero1)
            hero2_idx = next(i for i, h in enumerate(hero_pool) if h["id"] == hero2)
            
            matchup_score = game_tree.matchup_matrix[hero1_idx, hero2_idx]
            
            if abs(matchup_score) > 0.1:  # Only include significant matchups
                hero1_obj = next(h for h in heroes if h.id == hero1)
                hero2_obj = next(h for h in heroes if h.id == hero2)
                
                key_matchups.append({
                    "hero1": {
                        "id": hero1,
                        "name": hero1_obj.name
                    },
                    "hero2": {
                        "id": hero2,
                        "name": hero2_obj.name
                    },
                    "advantage": matchup_score,
                    "favors": "team1" if matchup_score > 0 else "team2"
                })
    
    # Sort key matchups by absolute advantage
    key_matchups.sort(key=lambda x: abs(x["advantage"]), reverse=True)
    
    # Calculate confidence based on amount of data
    relevant_matches = sum(1 for m in match_data if any(h["hero_id"] in request.team1 for h in m["heroes"]) and any(h["hero_id"] in request.team2 for h in m["heroes"]))
    confidence = min(1.0, relevant_matches / 100)  # Scale confidence based on data volume
    
    result = {
        "win_probability": win_probability,
        "confidence": confidence,
        "key_matchups": key_matchups[:5]  # Return top 5 matchups
    }
    
    # Cache the result
    redis_client.setex(cache_key, 3600, json.dumps(result))  # Cache for 1 hour
    
    return result

@router.post("/counter-team", response_model=CounterTeamResponse)
def recommend_counter_team(
    request: CounterTeamRequest,
    db: Session = Depends(get_db)
):
    # Validate hero IDs
    all_heroes = db.query(models.Hero).all()
    hero_id_set = set(h.id for h in all_heroes)
    
    for hero_id in request.enemy_team:
        if hero_id not in hero_id_set:
            raise HTTPException(status_code=400, detail=f"Invalid hero ID: {hero_id}")
    
    # Set available heroes if not provided
    available_heroes = request.available_heroes or list(hero_id_set)
    
    # Get all matches for analysis
    matches = db.query(models.Match).all()
    match_heroes = db.query(models.MatchHero).all()
    
    # Format match data for analysis
    match_data = []
    for match in matches:
        heroes = [
            {
                "hero_id": mh.hero_id,
                "team": mh.team
            }
            for mh in match_heroes if mh.match_id == match.id
        ]
        
        match_data.append({
            "id": match.id,
            "winner_team": match.winner_team,
            "heroes": heroes
        })
    
    # Get hero data
    hero_pool = [{"id": h.id, "name": h.name} for h in all_heroes]
    
    # Initialize game tree analysis
    game_tree = GameTreeAnalysis(hero_pool)
    game_tree.initialize_matchup_matrix(match_data)
    
    # Find optimal counter team
    recommended_team = game_tree.find_optimal_counter(request.enemy_team, available_heroes)
    
    # Predict win probability
    win_probability = game_tree.predict_matchup(recommended_team, request.enemy_team)
    
    # Generate explanations
    hero_explanations = []
    for hero_id in recommended_team:
        hero = next(h for h in all_heroes if h.id == hero_id)
        
        # Find which enemy heroes this hero counters
        countered_heroes = []
        for enemy_id in request.enemy_team:
            hero_idx = next(i for i, h in enumerate(hero_pool) if h["id"] == hero_id)
            enemy_idx = next(i for i, h in enumerate(hero_pool) if h["id"] == enemy_id)
            
            matchup_score = game_tree.matchup_matrix[hero_idx, enemy_idx]
            
            if matchup_score > 0.1:  # Significant advantage
                enemy_hero = next(h for h in all_heroes if h.id == enemy_id)
                countered_heroes.append({
                    "id": enemy_id,
                    "name": enemy_hero.name,
                    "advantage": matchup_score
                })
        
        hero_explanations.append({
            "id": hero_id,
            "name": hero.name,
            "counters": countered_heroes,
            "overall_value": sum(c["advantage"] for c in countered_heroes)
        })
    
    # Sort explanations by overall value
    hero_explanations.sort(key=lambda x: x["overall_value"], reverse=True)
    
    return {
        "recommended_team": recommended_team,
        "win_probability": win_probability,
        "hero_explanations": hero_explanations
    } 