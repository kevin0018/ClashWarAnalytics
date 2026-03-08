from src.config import Config
from src.api.client import CoCClient
from src.logic.analyzer import WarAnalyzer
from src.report.excel import ExcelReporter
from src.upload_drive import update_file
from src.notifications import send_telegram_message
import os
import sys
import time
import pandas as pd

SERVICE_ACCOUNT_FILE = "service_account.json"

def main():
    print("[INFO] Starting ClashWarAnalytics ETL Pipeline (Multi-Clan)...")

    # Verificación temprana: sin service_account.json no se puede subir a Drive
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        error_msg = (
            f"<b>Error de configuración</b>\n\n"
            f"Falta el archivo <code>{SERVICE_ACCOUNT_FILE}</code>.\n"
            f"Sin él no se puede subir el Excel a Google Drive. "
            f"Revisa la configuración en el servidor (VPS)."
        )
        print(f"[ERROR] '{SERVICE_ACCOUNT_FILE}' no encontrado. No se puede subir a Drive.")
        try:
            send_telegram_message(error_msg)
        except Exception:
            pass
        sys.exit(1)

    # Initialize API Client
    client = CoCClient()
    
    # Flag to track if we actually generated any new report to upload
    files_updated = False
    
    # Lists to track status for the notification
    generated_clans = []
    skipped_clans = []

    # --- CLAN LOOP ---
    for clan_tag in Config.CLAN_TAGS:
        clan_tag = clan_tag.strip()
        
        print("\n---------------------------------------------------")
        print(f"[INFO] Processing Clan Tag: {clan_tag}")
        print("---------------------------------------------------")

        # 1. Fetch Basic Clan Data
        clan_info = client.get_clan_info(clan_tag)
        
        if not clan_info:
            print(f"[ERROR] Could not fetch clan info for {clan_tag}. Skipping.")
            continue

        # Extract Clan Name
        clan_name = clan_info.get('name', 'Clan')
        member_list = clan_info.get('memberList', [])
        print(f"[INFO] Clan '{clan_name}' roster loaded: {len(member_list)} members.")

        # 2. Initialize Analyzer
        analyzer = WarAnalyzer(member_list)

        # 3. Fetch League Group
        league_group = client.get_league_group(clan_tag)
        
        if not league_group or 'rounds' not in league_group:
            print(f"[WARN] {clan_name} ({clan_tag}) is not in an active CWL group. Skipping.")
            skipped_clans.append(f"{clan_name} (No CWL)")
            continue

        rounds = league_group['rounds']
        print(f"[INFO] Found {len(rounds)} rounds to process.")

        # Flag for THIS specific clan
        is_cwl_complete = False 
        
        # 4. Process Rounds
        for i, round_data in enumerate(rounds):
            war_tags = round_data.get('warTags', [])
            found_our_war = False
            
            for war_tag in war_tags:
                if war_tag == "#0": continue 
                
                # Fetch war details
                war_data = client._get(f"/clanwarleagues/wars/{war_tag.replace('#', '%23')}")
                
                if not war_data: continue

                # Check if this war involves the current clan
                clan_tag_in_war = war_data.get('clan', {}).get('tag')
                opponent_tag_in_war = war_data.get('opponent', {}).get('tag')
                
                if clan_tag_in_war == clan_tag or opponent_tag_in_war == clan_tag:
                    state = war_data.get('state')
                    print(f"   > Round {i+1}: {state}")
                    analyzer.process_round(war_data, clan_tag)
                    
                    # Check if Round 7 has ended
                    if i == 6:
                        if state == 'warEnded':
                            is_cwl_complete = True
                        else:
                            print(f"   [INFO] Round 7 found but state is '{state}'. CWL not finished.")
                    
                    found_our_war = True
                    break 
            
            if not found_our_war:
                print(f"   > Round {i+1}: No data or Prep Day.")
            
            time.sleep(0.5)

        # 5. Generate Excel for this Clan
        if is_cwl_complete:
            print(f"[INFO] CWL Completed for {clan_name}. Generating Excel sheet...")
            
            # Sort by Net Balance
            sorted_stats = analyzer.get_sorted_stats(sort_by="net_balance")
            
            # Generate Excel
            output_filename = "CWL_History.xlsx"
            ExcelReporter.generate(sorted_stats, clan_name, output_filename)
            
            files_updated = True
            generated_clans.append(clan_name)
        else:
            print(f"[STOP] Report skipped for {clan_name} (CWL incomplete).")
            skipped_clans.append(clan_name)

    # --- UPLOAD & NOTIFICATION PHASE ---
    
    date_str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")

    if files_updated:
        print("\n[INFO] Reports generated. Initiating Drive upload...")
        try:
            update_file()
            
            # --- SUCCESS NOTIFICATION ---
            clans_str = ", ".join(generated_clans)
            
            msg = (
                f"<b>CWL Report Generated</b>\n\n"
                f"Clans: {clans_str}\n"
                f"Date: {date_str}\n"
                f"Status: Success. File updated on Google Drive."
            )
            send_telegram_message(msg)
            
        except Exception as e:
            print(f"[ERROR] Drive upload failed. Error: {e}")
            
            # --- CRITICAL ERROR NOTIFICATION ---
            error_msg = f"<b>Critical Error</b>\nDrive upload failed:\n{str(e)}"
            send_telegram_message(error_msg)
            
    else:
        print("\n[INFO] No new reports were generated. Drive upload skipped.")
        
        # --- INFO NOTIFICATION (WAITING) ---
        # This tells you the script ran but there was nothing to do yet.
        if skipped_clans:
            skipped_str = ", ".join(skipped_clans)
            msg = (
                f"<b>CWL Script Executed - No Changes</b>\n\n"
                f"Clans Checked: {skipped_str}\n"
                f"Date: {date_str}\n"
                f"Status: CWL not finished yet. Waiting for Round 7 end."
            )
            send_telegram_message(msg)

    print("[DONE] Pipeline finished.")

if __name__ == "__main__":
    main()