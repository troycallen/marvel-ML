from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Hero(Base):
    __tablename__ = "heroes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    role = Column(String)
    abilities = Column(JSON)
    win_rate = Column(Float, default=0.0)
    pick_rate = Column(Float, default=0.0)
    
    # Relationships
    match_heroes = relationship("MatchHero", back_populates="hero")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer)  # in seconds
    winner_team = Column(Integer)  # 1 or 2
    map = Column(String)
    
    # Relationships
    heroes = relationship("MatchHero", back_populates="match")

class MatchHero(Base):
    __tablename__ = "match_heroes"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    hero_id = Column(Integer, ForeignKey("heroes.id"))
    player_id = Column(String, index=True)
    team = Column(Integer)  # 1 or 2
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    damage_dealt = Column(Integer, default=0)
    
    # Relationships
    match = relationship("Match", back_populates="heroes")
    hero = relationship("Hero", back_populates="match_heroes")

class TeamComposition(Base):
    __tablename__ = "team_compositions"
    
    id = Column(Integer, primary_key=True, index=True)
    heroes = Column(JSON)  # List of hero IDs
    win_count = Column(Integer, default=0)
    loss_count = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    nash_equilibrium_value = Column(Float, nullable=True) 