import pandas as pd
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class MarvelRivalsTransformer:
    def __init__(self):
        pass
    
    def transform_match_data(self, raw_matches: List[Dict]) -> List[Dict]:
        """Transform raw match data into a format suitable for analysis"""
        transformed_matches = []
        
        for match in raw_matches:
            try:
                # Extract basic match info
                transformed_match = {
                    "match_id": match["id"],
                    "timestamp": match["timestamp"],
                    "duration": match["duration"],
                    "winner_team": match["winner_team"],
                    "map": match["map"],
                    "heroes": []
                }
                
                # Process hero data
                for player in match["players"]:
                    hero_data = {
                        "hero_id": player["hero_id"],
                        "player_id": player["player_id"],
                        "team": player["team"],
                        "kills": player["stats"]["kills"],
                        "deaths": player["stats"]["deaths"],
                        "assists": player["stats"]["assists"],
                        "damage_dealt": player["stats"]["damage_dealt"]
                    }
                    transformed_match["heroes"].append(hero_data)
                
                transformed_matches.append(transformed_match)
            except KeyError as e:
                logger.error(f"Error transforming match data: {e}")
                continue
        
        return transformed_matches
    
    def calculate_hero_stats(self, matches: List[Dict]) -> Dict[int, Dict]:
        """Calculate statistics for each hero based on match data"""
        hero_stats = {}
        
        # Initialize counters
        for match in matches:
            for hero in match["heroes"]:
                hero_id = hero["hero_id"]
                if hero_id not in hero_stats:
                    hero_stats[hero_id] = {
                        "games_played": 0,
                        "wins": 0,
                        "losses": 0,
                        "kills": 0,
                        "deaths": 0,
                        "assists": 0,
                        "damage_dealt": 0
                    }
        
        # Aggregate stats
        for match in matches:
            winner_team = match["winner_team"]
            for hero in match["heroes"]:
                hero_id = hero["hero_id"]
                team = hero["team"]
                
                hero_stats[hero_id]["games_played"] += 1
                if team == winner_team:
                    hero_stats[hero_id]["wins"] += 1
                else:
                    hero_stats[hero_id]["losses"] += 1
                
                hero_stats[hero_id]["kills"] += hero["kills"]
                hero_stats[hero_id]["deaths"] += hero["deaths"]
                hero_stats[hero_id]["assists"] += hero["assists"]
                hero_stats[hero_id]["damage_dealt"] += hero["damage_dealt"]
        
        # Calculate derived metrics
        for hero_id, stats in hero_stats.items():
            games_played = stats["games_played"]
            if games_played > 0:
                stats["win_rate"] = stats["wins"] / games_played
                stats["kda"] = (stats["kills"] + stats["assists"]) / max(1, stats["deaths"])
                stats["avg_damage"] = stats["damage_dealt"] / games_played
            else:
                stats["win_rate"] = 0
                stats["kda"] = 0
                stats["avg_damage"] = 0
        
        return hero_stats
    
    def identify_team_compositions(self, matches: List[Dict]) -> List[Dict]:
        """Identify and analyze team compositions from match data"""
        team_comps = {}
        
        for match in matches:
            winner_team = match["winner_team"]
            
            # Extract team compositions
            team1_heroes = sorted([h["hero_id"] for h in match["heroes"] if h["team"] == 1])
            team2_heroes = sorted([h["hero_id"] for h in match["heroes"] if h["team"] == 2])
            
            # Create composition keys
            team1_key = ",".join(map(str, team1_heroes))
            team2_key = ",".join(map(str, team2_heroes))
            
            # Update team1 stats
            if team1_key not in team_comps:
                team_comps[team1_key] = {"heroes": team1_heroes, "wins": 0, "losses": 0}
            if winner_team == 1:
                team_comps[team1_key]["wins"] += 1
            else:
                team_comps[team1_key]["losses"] += 1
            
            # Update team2 stats
            if team2_key not in team_comps:
                team_comps[team2_key] = {"heroes": team2_heroes, "wins": 0, "losses": 0}
            if winner_team == 2:
                team_comps[team2_key]["wins"] += 1
            else:
                team_comps[team2_key]["losses"] += 1
        
        # Calculate win rates
        for comp_key, comp_data in team_comps.items():
            total_games = comp_data["wins"] + comp_data["losses"]
            if total_games > 0:
                comp_data["win_rate"] = comp_data["wins"] / total_games
                comp_data["total_games"] = total_games
            else:
                comp_data["win_rate"] = 0
                comp_data["total_games"] = 0
        
        # Convert to list and sort by total games
        team_comp_list = list(team_comps.values())
        team_comp_list.sort(key=lambda x: x["total_games"], reverse=True)
        
        return team_comp_list 