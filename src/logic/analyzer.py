from typing import List, Dict, Optional
from src.models import PlayerStats

class WarAnalyzer:
    """
    Engine that processes raw Clan War League data to extract insights.
    """

    def __init__(self, members: List[Dict]):
        # Initialize stats registry with current clan members
        self.stats: Dict[str, PlayerStats] = {}
        self._initialize_roster(members)

    def _initialize_roster(self, members: List[Dict]):
        """Creates an empty database for all roster members."""
        for member in members:
            tag = member.get('tag')
            name = member.get('name')
            th_level = member.get('townHallLevel', 0)
            
            self.stats[tag] = PlayerStats(
                tag=tag,
                name=name,
                town_hall_level=th_level
            )

    def process_round(self, war_data: Dict, my_clan_tag: str):
        """
        Processes a full war round (Offense and Defense).
        """
        if war_data.get('state') == 'notInWar':
            return

        # Identify which clan is ours
        if war_data['clan']['tag'] == my_clan_tag:
            my_clan = war_data['clan']
            enemy_clan = war_data['opponent']
        else:
            my_clan = war_data['opponent']
            enemy_clan = war_data['clan']

        # 1. Process OFFENSE (Our attacks)
        for member in my_clan.get('members', []):
            tag = member.get('tag')
            
            # Only process if member is in our initial roster
            if tag in self.stats:
                attacks = member.get('attacks', [])
                if attacks:
                    self.stats[tag].attacks_used += len(attacks)
                    
                    # Sum raw totals
                    self.stats[tag].stars_earned += sum(a['stars'] for a in attacks)
                    self.stats[tag].destruction_percentage += sum(a['destructionPercentage'] for a in attacks)
                    
                    # Detailed Star Breakdown (Leader's request)
                    for attack in attacks:
                        stars = attack['stars']
                        if stars == 3:
                            self.stats[tag].three_star_count += 1
                        elif stars == 2:
                            self.stats[tag].two_star_count += 1
                        elif stars == 1:
                            self.stats[tag].one_star_count += 1
                        else:
                            self.stats[tag].zero_star_count += 1

        # 2. Process DEFENSE (Stars conceded)
        # We iterate through ENEMY members and check who they attacked
        for enemy in enemy_clan.get('members', []):
            for attack in enemy.get('attacks', []):
                defender_tag = attack.get('defenderTag')
                
                # If the defender is one of ours, log the damage
                if defender_tag in self.stats:
                    self.stats[defender_tag].defense_count += 1
                    self.stats[defender_tag].stars_conceded += attack['stars']
                    self.stats[defender_tag].destruction_received += attack['destructionPercentage']

    def get_sorted_stats(self, sort_by: str = "net_balance") -> List[PlayerStats]:
        """Returns the list of stats sorted by the given criteria."""
        all_stats = list(self.stats.values())
        
        if sort_by == "net_balance":
            # Sort by Net Balance (High to Low)
            return sorted(all_stats, key=lambda x: x.net_balance, reverse=True)
        elif sort_by == "stars_conceded":
            # Sort by Defense Fails (High to Low) - Who conceded the most
            return sorted(all_stats, key=lambda x: x.stars_conceded, reverse=True)
        
        return all_stats