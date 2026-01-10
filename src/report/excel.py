import pandas as pd
import os
import re

class ExcelReporter:
    @staticmethod
    def generate(data: list, clan_name: str, filename: str = "CWL_History.xlsx"):
        
        # --- 1. DATA PREPARATION ---
        df = pd.DataFrame([vars(d) for d in data])
        
        # --- FILTERING ---
        # Filter out inactive players
        if 'attacks_used' in df.columns and 'defense_count' in df.columns:
            df = df[(df['attacks_used'] > 0) | (df['defense_count'] > 0)]
        
        if df.empty:
            print(f"[WARN] No active data for clan: {clan_name}.")
            return

        # --- NET BALANCE CALCULATION ---
        # Calculate Net Balance
        if 'stars_earned' in df.columns and 'stars_conceded' in df.columns:
            df['net_balance'] = df['stars_earned'] - df['stars_conceded']

        # --- COLUMN MAPPING ---
        # Map columns
        columns_map = {
            'name': 'Jugador',
            'town_hall_level': 'TH',
            'attacks_used': 'Ataques',
            'three_star_count': '3 Estrellas',
            'two_star_count': '2 Estrellas',
            'one_star_count': '1 Estrella',
            'zero_star_count': '0 Estrellas',
            'stars_earned': 'Estrellas Atq.',
            'avg_destruction': 'Destr %',
            'avg_stars_attack': 'Prom. Atq',
            'defense_count': 'Defensas',
            'stars_conceded': 'Estrellas Def.',
            'avg_stars_defense': 'Prom. Def',
            'avg_destruction_defense': '% Dest. Recib.',
            'net_balance': 'Balance Neto'
        }
        
        # --- SELECTING AND RENAMING COLUMNS ---
        # Select and rename columns
        cols_to_use = [c for c in columns_map.keys() if c in df.columns]
        df = df[cols_to_use].rename(columns=columns_map)
        
        # --- COLUMN ORDERING ---
        # Specific column ordering
        target_order = [
            'Jugador',
            'TH',
            'Ataques',
            '3 Estrellas',
            '2 Estrellas',
            '1 Estrella',
            '0 Estrellas',
            'Estrellas Atq.',
            'Destr %',
            'Prom. Atq',
            'Defensas',
            'Estrellas Def.',
            'Prom. Def',
            '% Dest. Recib.',
            'Balance Neto'
        ]
        
        # --- COLUMN EXISTENCE CHECK ---
        # Ensure we only request columns that exist in the DF
        df = df[[col for col in target_order if col in df.columns]]

        # --- PERCENTAGE CONVERSION ---
        # Convert percentages to decimals
        cols_percent = ['Destr %', '% Dest. Recib.']
        for col in cols_percent:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0

        # --- SAFE SHEET NAME GENERATION ---
        # Generate safe sheet name
        safe_clan = "".join([c for c in clan_name if c.isalnum() or c in (' ', '_')]).strip()
        month = pd.Timestamp.now().strftime("%b %Y")
        sheet_name = f"{safe_clan} {month}"[:31]

        # --- 2. SHEET MANAGEMENT ---
        # Manage sheets
        all_sheets = {}
        if os.path.exists(filename):
            try:
                all_sheets = pd.read_excel(filename, sheet_name=None)
            except Exception as e:
                print(f"[INFO] Could not read existing file (creating new): {e}")

        all_sheets[sheet_name] = df

        # --- 3. WRITING WITH XLSXWRITER ---
        # Write with XlsxWriter
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            workbook = writer.book

            # --- GLOBAL FORMATS ---
            # Global formats
            fmt_percent = workbook.add_format({'num_format': '0.00%', 'align': 'center', 'valign': 'vcenter'})
            fmt_decimal = workbook.add_format({'num_format': '0.00', 'align': 'center', 'valign': 'vcenter'})
            fmt_center  = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            
            # --- HEADER AND ALTERNATE ROW FORMATS ---
            # Formats for header and alternate rows
            fmt_header = workbook.add_format({
                'bold': True,
                'font_color': '#FFFFFF',
                'bg_color': '#356854',
                'align': 'center',
                'valign': 'vcenter'
            })
            fmt_row_odd = workbook.add_format({'bg_color': '#f6f8f9', 'align': 'center', 'valign': 'vcenter'})
            fmt_row_even = workbook.add_format({'bg_color': '#ffffff', 'align': 'center', 'valign': 'vcenter'})
            
            # Formatos combinados para columnas específicas con fondos de fila
            fmt_percent_odd = workbook.add_format({'num_format': '0.00%', 'align': 'center', 'valign': 'vcenter', 'bg_color': '#f6f8f9'})
            fmt_percent_even = workbook.add_format({'num_format': '0.00%', 'align': 'center', 'valign': 'vcenter', 'bg_color': '#ffffff'})
            fmt_decimal_odd = workbook.add_format({'num_format': '0.00', 'align': 'center', 'valign': 'vcenter', 'bg_color': '#f6f8f9'})
            fmt_decimal_even = workbook.add_format({'num_format': '0.00', 'align': 'center', 'valign': 'vcenter', 'bg_color': '#ffffff'})
            fmt_center_odd = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#f6f8f9'})
            fmt_center_even = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#ffffff'})
            fmt_left_odd = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bg_color': '#f6f8f9'})
            fmt_left_even = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bg_color': '#ffffff'})
            
            for name, sheet_df in all_sheets.items():
                # Write data without header (the table will put the header)
                sheet_df.to_excel(writer, sheet_name=name, index=False, startrow=1, header=False)
                
                ws = writer.sheets[name]
                (rows_count, cols_count) = sheet_df.shape
                
                # --- TABLE COORDINATES ---
                # Coordinates of the table
                table_last_row = rows_count
                table_last_col = cols_count - 1

                column_settings = [{'header': col_name} for col_name in sheet_df.columns]
                clean_name = re.sub(r'[^A-Za-z0-9]', '', name)
                table_name = f"Tbl_{clean_name}"

                # --- CRITICAL CORRECTION: HYBRID STRATEGY ---
                
                # 1. Add Table (Disabling internal filter with 'autofilter': False)
                # We use a minimum style to not interfere with our custom colors
                ws.add_table(0, 0, table_last_row, table_last_col, {
                    'name': table_name,
                    'columns': column_settings,
                    'style': 'Table Style Light 1',  # Minimum style
                    'autofilter': False,
                    'banded_rows': False  # Disable to apply our custom colors
                })

                # 2. Add Sheet Autofilter (This is the one Google Sheets reads)
                ws.autofilter(0, 0, table_last_row, table_last_col)
                
                # 3. Apply custom format to header
                for col_idx in range(cols_count):
                    ws.write(0, col_idx, sheet_df.columns[col_idx], fmt_header)

                # --- 4. VISUAL FORMATS ---
                # Apply formats to columns and alternate rows
                for i, col in enumerate(sheet_df.columns):
                    max_len = max(
                        len(str(col)), 
                        sheet_df[col].astype(str).map(len).max() if not sheet_df[col].empty else 0
                    )
                    width = max_len + 4

                    # Apply width format (the row formats are applied after)
                    ws.set_column(i, i, width)

                # Apply format to alternate rows (odd #f6f8f9, even #ffffff)
                # The data starts in row 1 (0-indexed), so row 1 = first row = odd
                for row_idx in range(1, rows_count + 1):
                    is_odd = (row_idx - 1) % 2 == 0
                    for col_idx, col in enumerate(sheet_df.columns):
                        cell_value = sheet_df.iloc[row_idx - 1, col_idx]
                        # Select format according to column type and row parity
                        if col in ['Destr %', '% Dest. Recib.']:
                            cell_fmt = fmt_percent_odd if is_odd else fmt_percent_even
                        elif col in ['Prom. Atq', 'Prom. Def']:
                            cell_fmt = fmt_decimal_odd if is_odd else fmt_decimal_even
                        elif col == 'Jugador':
                            cell_fmt = fmt_left_odd if is_odd else fmt_left_even
                        else:
                            cell_fmt = fmt_center_odd if is_odd else fmt_center_even
                        ws.write(row_idx, col_idx, cell_value, cell_fmt)

                # --- CONDITIONAL FORMAT ---
                # Conditional format (Traffic Light)
                if 'Balance Neto' in sheet_df.columns:
                    net_idx = sheet_df.columns.get_loc('Balance Neto')
                    ws.conditional_format(1, net_idx, table_last_row, net_idx, {
                        'type': '3_color_scale',
                        'min_color': '#F8696B', # Red
                        'mid_color': '#FFFFFF', # White
                        'max_color': '#63BE7B'  # Green
                    })

        print(f"[EXCEL] Report generated successfully: {filename}")
