from src.config import Config
from src.api.client import CoCClient
from src.logic.analyzer import WarAnalyzer
from src.report.excel import ExcelReporter
import time

def main():
    print("[INFO] Starting ClashWaralytics ETL Pipeline...")
    
    # 1. Initialize API Client
    client = CoCClient()
    
    # 2. Fetch Basic Clan Data (To get the Roster)
    print(f"[INFO] Fetching clan details for {Config.CLAN_TAG}...")
    clan_info = client.get_clan_info(Config.CLAN_TAG)
    
    if not clan_info:
        print("[ERROR] Could not fetch clan info. Aborting.")
        return

    # Use 'memberList' correctly as per API response
    member_list = clan_info.get('memberList', [])
    print(f"[INFO] Clan Roster loaded: {len(member_list)} members.")

    # 3. Initialize Analyzer with the roster
    analyzer = WarAnalyzer(member_list)

    # 4. Fetch League Group
    print("[INFO] Fetching CWL Group Data...")
    league_group = client.get_league_group(Config.CLAN_TAG)
    
    if not league_group or 'rounds' not in league_group:
        print("[ERROR] No active CWL group found. Is the clan in a league?")
        return

    rounds = league_group['rounds']
    print(f"[INFO] Found {len(rounds)} rounds to process.")

    # 5. Loop through rounds and process wars
    for i, round_data in enumerate(rounds):
        war_tags = round_data.get('warTags', [])
        
        found_our_war = False
        
        # Iterate through the 4 wars in the group round to find ours
        for war_tag in war_tags:
            if war_tag == "#0": 
                continue # War not generated yet
            
            # Fetch war details
            war_data = client._get(f"/clanwarleagues/wars/{war_tag.replace('#', '%23')}")
            
            if not war_data:
                continue

            # Identify if this war belongs to our clan
            clan_tag_in_war = war_data.get('clan', {}).get('tag')
            opponent_tag_in_war = war_data.get('opponent', {}).get('tag')
            
            if clan_tag_in_war == Config.CLAN_TAG or opponent_tag_in_war == Config.CLAN_TAG:
                print(f"   > Processing Round {i+1} (State: {war_data.get('state')})")
                analyzer.process_round(war_data, Config.CLAN_TAG)
                found_our_war = True
                break # Stop searching this round, move to next
        
        if not found_our_war:
            print(f"   > Round {i+1}: No active war data found (or Preparation Day).")
        
        # Rate limit protection
        time.sleep(0.5)

    # 6. Generate Report
    print("[INFO] Processing finished. Generating Excel report...")
    
    # Sort data by Net Balance (Top performers first)
    sorted_stats = analyzer.get_sorted_stats(sort_by="net_balance")
    
    # This filename will persist. New months will be added as new sheets.
    output_filename = "CWL_History.xlsx"
    ExcelReporter.generate(sorted_stats, output_filename)
    
    print("[DONE] Pipeline finished successfully.")

if __name__ == "__main__":
    main()