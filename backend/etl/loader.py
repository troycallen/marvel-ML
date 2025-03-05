from sqlalchemy.orm import Session
from typing import List, Dict
import logging
from app import models

logger = logging.getLogger(__name__)

class MarvelRivalsLoader:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def load_matches(self, transformed_matches: List[Dict]) -> int:
        """Load transformed match data into the database"""
        matches_loaded = 0
        
        for match_data in transformed_matches:
            try:
                # Check if match already exists
                existing_match = self.db.query(models.Match).filter_by(
                    match_id=match_data["match_id"]
                ).first()
                
                if existing_match:
                    logger.info(f"Match {match_data['match_id']} already exists, skipping")
                    continue
                
                # Create new match
                new_match = models.Match(
                    match_id=match_data["match_id"],
                    timestamp=match_data["timestamp"],
                    duration=match_data["duration"],
                    winner_team=match_data["winner_team"],
                    map=match_data["map"]
                )
                
                self.db.add(new_match)
                self.db.flush()  # Get the ID without committing
                
                # Add hero data
                for hero_data in match_data["heroes"]:
                    match_hero = models.MatchHero(
                        match_id=new_match.id,
                        hero_id=hero_data["hero_id"],
                        player_id=hero_data["player_id"],
                        team=hero_data["team"],
                        kills=hero_data["kills"],
                        deaths=hero_data["deaths"],
                        assists=hero_data["assists"],
                        damage_dealt=hero_data["damage_dealt"]
                    )
                    self.db.add(match_hero)
                
                matches_loaded += 1
            except Exception as e:
                logger.error(f"Error loading match {match_data.get('match_id', 'unknown')}: {e}")
                self.db.rollback()
                continue
        
        self.db.commit()
        return matches_loaded
    
    def update_hero_stats(self, hero_stats: Dict[int, Dict]) -> int:
        """Update hero statistics in the database"""
        heroes_updated = 0
        
        for hero_id, stats in hero_stats.items():
            try:
                hero = self.db.query(models.Hero).filter_by(id=hero_id).first()
                
                if not hero:
                    logger.warning(f"Hero with ID {hero_id} not found, skipping stats update")
                    continue
                
                hero.win_rate = stats["win_rate"]
                hero.pick_rate = stats["games_played"] / 100  # Normalize based on total matches
                
                heroes_updated += 1
            except Exception as e:
                logger.error(f"Error updating stats for hero {hero_id}: {e}")
                continue
        
        self.db.commit()
        return heroes_updated
    
    def load_team_compositions(self, team_comps: List[Dict]) -> int:
        """Load team composition data into the database"""
        comps_loaded = 0
        
        # Clear existing compositions
        self.db.query(models.TeamComposition).delete()
        
        for comp_data in team_comps:
            try:
                new_comp = models.TeamComposition(
                    heroes=comp_data["heroes"],
                    win_count=comp_data["wins"],
                    loss_count=comp_data["losses"],
                    win_rate=comp_data["win_rate"]
                )
                
                self.db.add(new_comp)
                comps_loaded += 1
            except Exception as e:
                logger.error(f"Error loading team composition: {e}")
                continue
        
        self.db.commit()
        return comps_loaded 