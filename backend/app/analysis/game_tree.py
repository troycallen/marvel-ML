import numpy as np
import cupy as cp  # GPU acceleration library
from typing import List, Dict, Tuple

class GameTreeAnalysis:
    def __init__(self, hero_pool: List[Dict]):
        self.hero_pool = hero_pool
        self.hero_ids = [hero["id"] for hero in hero_pool]
        self.matchup_matrix = None
        
    def initialize_matchup_matrix(self, match_data: List[Dict]):
        """Initialize the matchup matrix from historical match data"""
        n = len(self.hero_ids)
        self.matchup_matrix = np.zeros((n, n), dtype=np.float32)
        
        # Process match data to build matchup matrix
        for match in match_data:
            winner_team = match["winner_team"]
            for hero1 in match["heroes"]:
                if hero1["team"] == winner_team:
                    for hero2 in match["heroes"]:
                        if hero2["team"] != winner_team:
                            idx1 = self.hero_ids.index(hero1["hero_id"])
                            idx2 = self.hero_ids.index(hero2["hero_id"])
                            self.matchup_matrix[idx1, idx2] += 1
                            self.matchup_matrix[idx2, idx1] -= 1
        
        # Normalize
        row_sums = self.matchup_matrix.sum(axis=1, keepdims=True)
        self.matchup_matrix = np.divide(self.matchup_matrix, row_sums, 
                                        out=np.zeros_like(self.matchup_matrix), 
                                        where=row_sums!=0)
    
    def predict_matchup(self, team1: List[int], team2: List[int]) -> float:
        """Predict win probability for team1 against team2"""
        # Convert to GPU arrays for acceleration
        team1_indices = [self.hero_ids.index(hero_id) for hero_id in team1]
        team2_indices = [self.hero_ids.index(hero_id) for hero_id in team2]
        
        # Transfer to GPU
        gpu_matchup_matrix = cp.asarray(self.matchup_matrix)
        
        # Calculate team vs team matchup score using GPU
        score = 0.0
        for i in team1_indices:
            for j in team2_indices:
                score += float(gpu_matchup_matrix[i, j])
        
        # Convert to win probability
        win_probability = 1 / (1 + np.exp(-score))
        return win_probability
    
    def find_optimal_counter(self, enemy_team: List[int], available_heroes: List[int]) -> List[int]:
        """Find optimal counter team composition using game tree analysis"""
        best_team = []
        best_score = float('-inf')
        
        # Number of heroes in a team
        team_size = 5
        
        # GPU acceleration for batch processing
        enemy_indices = [self.hero_ids.index(hero_id) for hero_id in enemy_team]
        available_indices = [self.hero_ids.index(hero_id) for hero_id in available_heroes 
                            if hero_id not in enemy_team]
        
        # Transfer to GPU
        gpu_matchup_matrix = cp.asarray(self.matchup_matrix)
        gpu_enemy_indices = cp.asarray(enemy_indices)
        
        # Pre-compute matchup scores for all available heroes against enemy team
        hero_scores = cp.zeros(len(available_indices), dtype=cp.float32)
        for i, hero_idx in enumerate(available_indices):
            hero_scores[i] = cp.sum(gpu_matchup_matrix[hero_idx, gpu_enemy_indices])
        
        # Convert back to CPU for team composition generation
        hero_scores_cpu = cp.asnumpy(hero_scores)
        
        # Sort heroes by their score against enemy team
        sorted_indices = np.argsort(-hero_scores_cpu)
        
        # Select top heroes as the counter team
        best_team = [available_heroes[available_indices.index(available_indices[idx])] 
                    for idx in sorted_indices[:team_size]]
        
        return best_team 