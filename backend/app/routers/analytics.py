from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database import get_db, redis_client
import json
from app import models
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

router = APIRouter()

class HeroStats(BaseModel):
    id: int
    name: str
    win_rate: float
    pick_rate: float
    kda: Optional[float] = None

class TeamCompStats(BaseModel):
    id: int
    heroes: List[int]
    win_rate: float
    total_games: int
    nash_equilibrium_value: Optional[float] = None

@router.get("/hero-stats", response_model=List[HeroStats])
def get_hero_stats(
    min_games: int = Query(10, description="Minimum games played"),
    db: Session = Depends(get_db)
):
    # Try to get from cache first
    cache_key = f"hero_stats:{min_games}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Query from database
    heroes = db.query(models.Hero).all()
    
    # Calculate additional stats
    result = []
    for hero in heroes:
        # Get match data for this hero
        match_heroes = db.query(models.MatchHero).filter(
            models.MatchHero.hero_id == hero.id
        ).all()
        
        if len(match_heroes) < min_games:
            continue
        
        # Calculate KDA
        kills = sum(mh.kills for mh in match_heroes)
        deaths = sum(mh.deaths for mh in match_heroes)
        assists = sum(mh.assists for mh in match_heroes)
        
        kda = (kills + assists) / max(1, deaths)
        
        result.append({
            "id": hero.id,
            "name": hero.name,
            "win_rate": hero.win_rate,
            "pick_rate": hero.pick_rate,
            "kda": kda
        })
    
    # Cache the result
    redis_client.setex(
        cache_key,
        timedelta(minutes=15).seconds,  # Cache for 15 minutes
        json.dumps(result)
    )
    
    return result

@router.get("/team-compositions", response_model=List[TeamCompStats])
def get_team_compositions(
    min_games: int = Query(5, description="Minimum games played"),
    db: Session = Depends(get_db)
):
    # Try to get from cache first
    cache_key = f"team_comps:{min_games}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Query from database
    team_comps = db.query(models.TeamComposition).all()
    
    # Filter and format
    result = []
    for comp in team_comps:
        total_games = comp.win_count + comp.loss_count
        
        if total_games < min_games:
            continue
        
        result.append({
            "id": comp.id,
            "heroes": comp.heroes,
            "win_rate": comp.win_rate,
            "total_games": total_games,
            "nash_equilibrium_value": comp.nash_equilibrium_value
        })
    
    # Sort by win rate
    result.sort(key=lambda x: x["win_rate"], reverse=True)
    
    # Cache the result
    redis_client.setex(
        cache_key,
        timedelta(minutes=30).seconds,  # Cache for 30 minutes
        json.dumps(result)
    )
    
    return result

@router.get("/win-rate-over-time")
def get_win_rate_over_time(
    hero_id: Optional[int] = None,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    query = db.query(
        models.Match.timestamp,
        models.MatchHero.hero_id,
        models.MatchHero.team,
        models.Match.winner_team
    ).join(
        models.MatchHero,
        models.Match.id == models.MatchHero.match_id
    ).filter(
        models.Match.timestamp >= start_date,
        models.Match.timestamp <= end_date
    )
    
    # Filter by hero if specified
    if hero_id is not None:
        query = query.filter(models.MatchHero.hero_id == hero_id)
    
    # Execute query
    matches = query.all()
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([
        {
            "date": match.timestamp.date(),
            "hero_id": match.hero_id,
            "won": match.team == match.winner_team
        }
        for match in matches
    ])
    
    if df.empty:
        return []
    
    # Group by date and calculate win rate
    if hero_id is not None:
        # Single hero analysis
        result = df.groupby("date").agg(
            games=("won", "count"),
            wins=("won", "sum")
        ).reset_index()
        
        result["win_rate"] = result["wins"] / result["games"]
        
        return result.to_dict(orient="records")
    else:
        # Overall win rate by hero
        result = df.groupby(["date", "hero_id"]).agg(
            games=("won", "count"),
            wins=("won", "sum")
        ).reset_index()
        
        result["win_rate"] = result["wins"] / result["games"]
        
        return result.to_dict(orient="records") 