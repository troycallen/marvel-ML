import numpy as np
from scipy.optimize import linprog

class TeamCompositionAnalyzer:
    def __init__(self, hero_pool):
        self.hero_pool = hero_pool
        self.payoff_matrix = None
    
    def build_payoff_matrix(self, match_history):
        """
        Builds payoff matrix from match history
        Returns: n x n matrix where n is number of possible team compositions
        """
        n = len(self.hero_pool)
        self.payoff_matrix = np.zeros((n, n))
        
        for match in match_history:
            team1_idx = self._get_team_index(match.team1)
            team2_idx = self._get_team_index(match.team2)
            if match.winner == 1:
                self.payoff_matrix[team1_idx][team2_idx] += 1
            else:
                self.payoff_matrix[team1_idx][team2_idx] -= 1
                
        return self.payoff_matrix
    
    def find_nash_equilibrium(self):
        """
        Implements Nash equilibrium using linear programming
        Returns: Optimal team composition probabilities
        """
        n = len(self.payoff_matrix)
        
        # Objective: maximize the minimum payoff
        c = np.array([-1] + [0] * n)
        
        # Constraints
        A_ub = np.vstack([-np.ones(n) - self.payoff_matrix.T,
                         -np.eye(n)])
        b_ub = np.zeros(2 * n)
        
        A_eq = np.array([[0] + [1] * n])
        b_eq = np.array([1])
        
        # Bounds
        bounds = [(None, None)] + [(0, 1)] * n
        
        # Solve linear program
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        
        return result.x[1:] if result.success else None 