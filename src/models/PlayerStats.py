from dataclasses import dataclass, field

@dataclass
class PlayerStats:
    """
    Represents the aggregated war statistics for a single clan member.
    """
    tag: str
    name: str
    town_hall_level: int
    
    # Offensive Stats (Detailed Breakdown)
    attacks_used: int = 0
    stars_earned: int = 0  # Total stars
    destruction_percentage: float = 0.0
    avg_stars_attack: float = 0.0
    avg_destruction: float = 0.0
    
    # Star Breakdown
    three_star_count: int = 0
    two_star_count: int = 0
    one_star_count: int = 0
    zero_star_count: int = 0
    
    # Defensive Stats
    stars_conceded: int = 0
    defense_count: int = 0
    destruction_received: float = 0.0
    avg_stars_defense: float = 0.0
    avg_destruction_defense: float = 0.0

    @property
    def net_balance(self) -> int:
        """
        Calculates the net star contribution.
        Formula: Stars Earned (Offense) - Stars Conceded (Defense)
        """
        return self.stars_earned - self.stars_conceded

    @property
    def average_destruction(self) -> float:
        """Calculates average destruction percentage per attack."""
        if self.attacks_used == 0:
            return 0.0
        return round(self.destruction_percentage / self.attacks_used, 2)
