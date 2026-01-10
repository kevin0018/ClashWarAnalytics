from typing import List, Dict
from src.models.PlayerStats import PlayerStats

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
            self.stats[tag] = PlayerStats(
                tag=tag,
                name=member.get('name'),
                town_hall_level=member.get('townHallLevel', 0)
            )

    def process_round(self, war_data: Dict, my_clan_tag: str):
        """
        Processes a full war round (Offense and Defense) and updates the stats database.
        """
        if war_data.get('state') == 'notInWar':
            return

        # Identify clans
        if war_data['clan']['tag'] == my_clan_tag:
            my_clan = war_data['clan']
            enemy_clan = war_data['opponent']
        else:
            my_clan = war_data['opponent']
            enemy_clan = war_data['clan']

        # Offense Processing
        for member in my_clan.get('members', []):
            tag = member.get('tag')
            
            # Only process if member is in our initial roster
            if tag in self.stats:
                attacks = member.get('attacks', [])
                if attacks:
                    self.stats[tag].attacks_used += len(attacks)
                    self.stats[tag].stars_earned += sum(a['stars'] for a in attacks)
                    # Accumulate raw percentage
                    self.stats[tag].destruction_percentage += sum(a['destructionPercentage'] for a in attacks)
                    
                    for attack in attacks:
                        s = attack['stars']
                        if s == 3: self.stats[tag].three_star_count += 1
                        elif s == 2: self.stats[tag].two_star_count += 1
                        elif s == 1: self.stats[tag].one_star_count += 1
                        else: self.stats[tag].zero_star_count += 1

        # Defense Processing
        for enemy in enemy_clan.get('members', []):
            for attack in enemy.get('attacks', []):
                defender_tag = attack.get('defenderTag')
                if defender_tag in self.stats:
                    self.stats[defender_tag].defense_count += 1
                    self.stats[defender_tag].stars_conceded += attack['stars']
                    self.stats[defender_tag].destruction_received += attack['destructionPercentage']

    def get_sorted_stats(self, sort_by: str = "net_balance") -> List[PlayerStats]:
        """Calculates averages and returns sorted list."""
        
        # --- CALCULATE AVERAGES BEFORE SORTING ---
        for member in self.stats.values():
            # --- OFENSIVA ---
            if member.attacks_used > 0:
                member.avg_stars_attack = round(member.stars_earned / member.attacks_used, 2)
                member.avg_destruction = round(member.destruction_percentage / member.attacks_used, 2)
            else:
                member.avg_stars_attack = 0.0
                member.avg_destruction = 0.0

            # --- DEFENSIVA ---
            if member.defense_count > 0:
                member.avg_stars_defense = round(member.stars_conceded / member.defense_count, 2)
                member.avg_destruction_defense = round(member.destruction_received / member.defense_count, 2)
            else:
                member.avg_stars_defense = None 
                member.avg_destruction_defense = None 

        # --- SORTING ---
        all_stats = list(self.stats.values())
        
        if sort_by == "net_balance":
            return sorted(all_stats, key=lambda x: x.net_balance, reverse=True)
        elif sort_by == "stars_conceded":
            return sorted(all_stats, key=lambda x: x.stars_conceded, reverse=True)
        
        return all_stats