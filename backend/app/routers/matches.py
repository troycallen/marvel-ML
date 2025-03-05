from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HeroStats(BaseModel):
    hero_id: int
    player_id: str
    team: int
    kills: int
    deaths: int
    assists: int
    damage_dealt: int

class MatchCreate(BaseModel):
    match_id: str
    duration: int
    winner_team: int
    map: str
    heroes: List[HeroStats]

class MatchResponse(BaseModel):
    id: int
    match_id: str
    timestamp: datetime
    duration: int
    winner_team: int
    map: str

@router.post("/", response_model=MatchResponse)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    db_match = models.Match(
        match_id=match.match_id,
        duration=match.duration,
        winner_team=match.winner_team,
        map=match.map
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    for hero_stat in match.heroes:
        db_match_hero = models.MatchHero(
            match_id=db_match.id,
            hero_id=hero_stat.hero_id,
            player_id=hero_stat.player_id,
            team=hero_stat.team,
            kills=hero_stat.kills,
            deaths=hero_stat.deaths,
            assists=hero_stat.assists,
            damage_dealt=hero_stat.damage_dealt
        )
        db.add(db_match_hero)
    
    db.commit()
    return db_match

@router.get("/recent", response_model=List[MatchResponse])
def get_recent_matches(limit: int = 10, db: Session = Depends(get_db)):
    matches = db.query(models.Match).order_by(models.Match.timestamp.desc()).limit(limit).all()
    return matches

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: str, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.match_id == match_id).first()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return match 