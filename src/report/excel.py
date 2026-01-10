import pandas as pd
import os
from datetime import datetime
from typing import List
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from src.models import PlayerStats

class ExcelReporter:
    """
    Handles the generation of Excel reports from processed stats.
    Supports appending new sheets to an existing history file.
    """

    @staticmethod
    def generate(stats: List[PlayerStats], filename: str):
        """
        Generates a styled Excel report. 
        Appends a new sheet with the current month/year name (e.g., 'Jan 2026').
        """
        
        # 1. SMART FILTERING
        # Remove inactive players (0 attacks AND 0 defenses).
        active_stats = [
            p for p in stats 
            if not (p.attacks_used == 0 and p.defense_count == 0)
        ]

        # 2. DATA MAPPING (Headers in Spanish)
        data = []
        for p in active_stats:
            data.append({
                "Nombre": p.name,
                "TH": p.town_hall_level,
                "Ataques": p.attacks_used,
                "3 Estrellas": p.three_star_count,
                "2 Estrellas": p.two_star_count,
                "1 Estrella": p.one_star_count,
                "0 Estrellas": p.zero_star_count,
                "Total (Of)": p.stars_earned,     # Offense Total
                "Total (Def)": p.stars_conceded,  # Defense Total
                "BALANCE NETO": p.net_balance     # The custom metric
            })

        if not data:
            print("[WARNING] No active players found to report.")
            return

        df = pd.DataFrame(data)

        # Reorder columns
        cols = [
            "Nombre", "TH", "Ataques", 
            "3 Estrellas", "2 Estrellas", "1 Estrella", "0 Estrellas", 
            "Total (Of)", "Total (Def)", "BALANCE NETO"
        ]
        # Safety check
        cols = [c for c in cols if c in df.columns]
        df = df[cols]

        # 3. DYNAMIC SHEET NAME
        current_sheet_name = datetime.now().strftime("%b %Y")

        # 4. DETERMINE WRITE MODE
        if os.path.exists(filename):
            print(f"[INFO] History file found. Appending sheet: '{current_sheet_name}'...")
            write_mode = 'a' 
            if_sheet_exists = 'replace'
        else:
            print(f"[INFO] Creating new history file: {filename}...")
            write_mode = 'w'
            if_sheet_exists = None

        try:
            writer_kwargs = {"engine": 'openpyxl', "mode": write_mode}
            if write_mode == 'a':
                writer_kwargs["if_sheet_exists"] = if_sheet_exists

            with pd.ExcelWriter(filename, **writer_kwargs) as writer:
                df.to_excel(writer, index=False, sheet_name=current_sheet_name)
                
                # --- APPLY STYLING ---
                ws = writer.sheets[current_sheet_name]
                
                # A. FORMAT HEADERS
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
                center_align = Alignment(horizontal="center")
                
                for cell in ws[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = center_align

                # B. AUTO-ADJUST COLUMN WIDTH
                # Iterate through columns to fit text
                for column_cells in ws.columns:
                    max_length = 0
                    column_letter = column_cells[0].column_letter
                    
                    for cell in column_cells:
                        try:
                            if cell.value:
                                cell_len = len(str(cell.value))
                                if cell_len > max_length:
                                    max_length = cell_len
                        except:
                            pass
                    
                    # Add extra padding (1.2 factor)
                    adjusted_width = (max_length + 2) * 1.2
                    ws.column_dimensions[column_letter].width = adjusted_width

                # C. CONDITIONAL FORMATTING
                last_row = ws.max_row
                
                # 1. NET BALANCE (Col J): 3-Color Scale
                ws.conditional_formatting.add(
                    f"J2:J{last_row}",
                    ColorScaleRule(
                        start_type="num", start_value=-5, start_color="F8696B", # Red
                        mid_type="num", mid_value=0, mid_color="FFFFFF",        # White
                        end_type="num", end_value=5, end_color="63BE7B"         # Green
                    )
                )

                # 2. DEFENSIVE STARS (Col I): Data Bar
                ws.conditional_formatting.add(
                    f"I2:I{last_row}",
                    DataBarRule(
                        start_type="min", end_type="max",
                        color="FF6347", showValue=True, minLength=None, maxLength=None
                    )
                )
                
                # D. CENTER ALIGNMENT FOR DATA
                for row in ws.iter_rows(min_row=2, max_row=last_row, min_col=2, max_col=10):
                    for cell in row:
                        cell.alignment = center_align

            print(f"[SUCCESS] Report updated successfully in: {filename}")
            
        except Exception as e:
            print(f"[ERROR] Failed to write Excel: {e}")
            print("[HINT] Make sure the Excel file is CLOSED before running the script.")