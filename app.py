import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import time
import io
import io
import uuid
import json

# ==============================================================================
# CONFIG & STYLE
# ==============================================================================
st.set_page_config(
    page_title="second-brain-core",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Esports Vibe (Dark + Gold/Black + Red Alerts)
st.markdown("""
<style>
    /* ========================================================================================= */
    /* GLOBAL THEME: SKY PROTOCOL - FUTURISTIC GLASSMORPHISM */
    /* ========================================================================================= */
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 1. Global Typography & Reset */
    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
    }

    /* 2. Main Background (Deep Galaxy) */
    .stApp {
        background-color: #05010d;
        background: radial-gradient(ellipse at 50% 0%, #2a0e45 0%, #0f051d 60%, #05010d 100%);
        background-attachment: fixed;
        color: #ffffff;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(123, 44, 191, 0.6);
    }
    
    p, label {
        color: #b0a8c9 !important; /* Muted Lavender */
    }

    /* 3. Sidebar (Dark Frosted Glass) */
    section[data-testid="stSidebar"] {
        background-color: rgba(20, 10, 35, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(123, 44, 191, 0.2);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }

    /* 4. Glass Cards & Metrics (The Core Look) */
    .glass-card, div[data-testid="stMetric"], div.block-container .stContainer, div.st-emotion-cache-1r6slb0 {
        background: rgba(30, 15, 55, 0.6);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 24px;
        border: 1px solid rgba(157, 78, 221, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
        padding: 24px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover, .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(123, 44, 191, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.1);
        border-color: rgba(157, 78, 221, 0.8);
    }

    /* Metric Typography */
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #b0a8c9 !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
    }
    
    div[data-testid="stMetricDelta"] {
        background: #1e0f37;
        padding: 4px 10px;
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 5. Buttons (Neon Gradient) */
    .stButton > button {
        background: linear-gradient(90deg, #7b2cbf 0%, #b5179e 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(123, 44, 191, 0.5) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(181, 23, 158, 0.7) !important;
        filter: brightness(1.2);
    }
    
    /* Secondary/Glass Button */
    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(157, 78, 221, 0.4) !important;
        box-shadow: none !important;
    }

    /* 6. Inputs (Futuristic form fields) */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background: rgba(15, 5, 29, 0.8) !important;
        border: 1px solid #4a2b7a !important;
        color: white !important;
        border-radius: 12px !important;
        }
    .stTextInput > div > div > input:focus, .stSelectbox > div > div > div:focus-within {
        border-color: #b5179e !important;
        box-shadow: 0 0 15px rgba(181, 23, 158, 0.3) !important;
    }

    /* 7. FAB (Floating Action Button) from previous task - refined */
    div[data-testid="stButton"] > button[kind="primary"] {
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        box-shadow: 0 0 25px rgba(247, 37, 133, 0.6) !important;
    }

    /* Mobile overrides */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2rem !important;
        }
        div[data-testid="stMetric"] {
            margin-bottom: 10px;
        }
    }
    /* Hero Card (Holographic/Cyberpunk Theme) */
    div[data-testid="stButton"] button.hero-card-btn {
        height: auto !important;
        white-space: pre-wrap !important;
        background: linear-gradient(135deg, rgba(30, 15, 55, 0.9), rgba(10, 5, 20, 0.95)) !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 16px !important;
        text-align: left !important;
        padding: 16px !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Hero Card (Minimalist Image-First Theme) */
    div[data-testid="stButton"] button.hero-card-btn {
        aspect-ratio: 3/4 !important;
        background: linear-gradient(135deg, #2c3e50, #000000) !important; /* Fallback */
        border: 1px solid #333 !important;
        border-radius: 15px !important;
        padding: 10px !important;
        width: 100% !important;
        
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-end !important; /* Text at bottom */
        align-items: center !important; /* Text centered */
        
        position: relative !important;
        overflow: hidden !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
    }

    /* Make the Markdown Image behave like a Background Image */
    div[data-testid="stButton"] button.hero-card-btn img {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        opacity: 0.7 !important; /* Dim image slightly so text pops */
        transition: opacity 0.3s ease, transform 0.5s ease !important;
        z-index: 1 !important;
    }
    
    /* Text Container (The paragraph inside button) */
    div[data-testid="stButton"] button.hero-card-btn p {
        position: relative !important;
        z-index: 2 !important;
        font-family: 'Inter', sans-serif !important;
        text-align: center !important;
        width: 100% !important;
        margin: 0 !important;
        padding-bottom: 5px !important;
        
        /* Gradient Overlay effect for readability at bottom */
        text-shadow: 0 2px 4px rgba(0,0,0,0.9) !important;
    }

    /* HEADER (Name) Styling via CSS ::first-line */
    div[data-testid="stButton"] button.hero-card-btn p::first-line {
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        line-height: 1.2 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* HOVER EFFECT */
    div[data-testid="stButton"] button.hero-card-btn:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 15px 30px rgba(0,0,0,0.6) !important;
        border-color: #aa22ff !important;
    }
    
    div[data-testid="stButton"] button.hero-card-btn:hover img {
        opacity: 0.9 !important; /* Brighten image on hover */
        transform: scale(1.05) !important; /* Subtle zoom */
    }
</style>
""",unsafe_allow_html=True)

# ==============================================================================
# BACKEND: GOOGLE SHEETS DB MANAGER
# ==============================================================================

@st.cache_data(ttl=3600)
def _fetch_versions_cached():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # Robust Client Access
        instance = conn._instance
        gspread_client = None
        if hasattr(instance, "client"):
            gspread_client = instance.client
        elif hasattr(instance, "_client"):
            gspread_client = instance._client
        elif hasattr(instance, "service_account"):
            gspread_client = instance.service_account
        
        client = gspread_client if gspread_client else instance
        
        sh = client.open_by_url(url)
        return [ws.title for ws in sh.worksheets()]
    except Exception:
        return ["VERSION 1.60.1.10"]

class DBManager:
    def __init__(self):
        # Initialize the GSheets connection
        self.conn = st.connection("gsheets", type=GSheetsConnection)

    def _get_spreadsheet(self):
        try:
            url = st.secrets["connections"]["gsheets"]["spreadsheet"]
            # Step 1: Access the internal instance
            instance = self.conn._instance
            
            # Step 2: Try to find the gspread client using the most common internal paths
            gspread_client = None
            if hasattr(instance, "client"):
                gspread_client = instance.client
            elif hasattr(instance, "_client"):
                gspread_client = instance._client
            elif hasattr(instance, "service_account"):
                gspread_client = instance.service_account
            
            # Step 3: If a client is found, use it to open the URL. 
            # Otherwise, try calling open_by_url on the instance directly as a last resort.
            if gspread_client:
                return gspread_client.open_by_url(url)
            else:
                return instance.open_by_url(url)
                
        except Exception as e:
            st.error(f"❌ Connection Failure: {e}")
            return None

    def get_all_versions(self):
        """Return a list of all worksheet titles (Versions)."""
        return _fetch_versions_cached()

    def create_version(self, new_version_name, clone_from_version=None):
        """
        Create a new worksheet (version).
        If clone_from_version is 'Empty' or None, create a fresh sheet with headers.
        Otherwise, duplicate the source sheet.
        """
        try:
            sh = self._get_spreadsheet()
            if sh is None:
                st.error("Cannot connect to Spreadsheet.")
                return False
            
            # Check if exists
            existing_titles = [ws.title for ws in sh.worksheets()]
            if new_version_name in existing_titles:
                st.error(f"Version '{new_version_name}' already exists!")
                return False
            
            if clone_from_version and clone_from_version != "Empty" and clone_from_version in existing_titles:
                # Clone Logic
                source_ws = sh.worksheet(clone_from_version)
                source_ws.duplicate(new_sheet_name=new_version_name)
            else:
                # Create Empty Logic
                new_ws = sh.add_worksheet(title=new_version_name, rows=100, cols=20)
                # CRITICAL: Write Headers immediately
                headers = ["name", "tier", "class", "position", "timing", "counters", "id", "image_url", "matchups"]
                new_ws.append_row(headers)
            
            # Clear cache to reflect new sheet
            st.cache_data.clear()
            return True

        except Exception as e:
            st.error(f"Failed to create version: {e}")
            return False

    def load_heroes(self, version_name="VERSION 1.60.1.10"):
        """Load heroes from the specified worksheet (version)."""
        try:
            # Read DataFrame using streamlit_gsheets with TTL cache
            df = self.conn.read(worksheet=version_name, ttl=3600)
            
            # Data Cleaning
            if df.empty:
                return pd.DataFrame(columns=["name", "tier", "class", "position", "timing", "counters", "id", "image_url", "matchups"])
            
            # 1. Drop rows with empty names (garbage data)
            if 'name' in df.columns:
                df = df.dropna(subset=['name'])
                df = df[df['name'].astype(str).str.strip() != '']
            
            # Handle NaN
            df = df.fillna("")
            
            # 2. Critical: Ensure Unique IDs
            # If 'id' column missing, create it
            if 'id' not in df.columns:
                df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                need_save = True
            else:
                # Convert to string and strip
                df['id'] = df['id'].astype(str).str.strip()
                pass

            # Detect duplicates or empty IDs
            seen_ids = set()
            need_save = False
            
            # Iterate and fix IDs in memory
            # We use a list to reconstruct the column to avoid index issues during iteration
            new_ids = []
            for idx, row in df.iterrows():
                row_id = row.get('id', '')
                
                # Check if invalid: empty, 'nan', or duplicate
                if not row_id or row_id.lower() == 'nan' or row_id in seen_ids:
                    # Generate new ID
                    new_id = str(uuid.uuid4())
                    new_ids.append(new_id)
                    seen_ids.add(new_id)
                    need_save = True
                else:
                    new_ids.append(row_id)
                    seen_ids.add(row_id)
            
            df['id'] = new_ids

            # Convert string representations of lists to actual lists if needed
            # (Assuming simple comma separation for storage simplicity in Sheets or manual entry)
            # If using JSON string storage:
            # df['counters'] = df['counters'].apply(lambda x: json.loads(x) if x else [])
            # For this simplified version, let's assume comma-separated strings for 'counters' and 'position' in loose usage,
            # BUT the previous code expected lists. Let's standadize:
            
            # 'counters': "HeroA, HeroB" -> ["HeroA", "HeroB"]
            if 'counters' in df.columns:
                 df['counters'] = df['counters'].astype(str).apply(
                     lambda x: [i.strip() for i in x.split(',')] if x.strip() else []
                 )
            
            # 'position': "Mid, Jungle" -> ["Mid", "Jungle"]
            if 'position' in df.columns:
                 df['position'] = df['position'].astype(str).apply(
                     lambda x: [i.strip() for i in x.split(',')] if x.strip() else []
                 )

            # 'matchups': JSON String -> List of Dicts
            if 'matchups' in df.columns:
                def parse_matchups(x):
                    try:
                        return json.loads(str(x)) if x and str(x).strip() else []
                    except:
                        return []
                df['matchups'] = df['matchups'].apply(parse_matchups)
            else:
                 df['matchups'] = [[] for _ in range(len(df))]
            
            # 3. Persist corrected IDs back to Sheet if changes were made
            if need_save:
                 # We need to perform a save operation without triggering infinite recursion or major overhead
                 # We reuse the logic from save_hero/update but for the whole DF
                 try:
                     output_df = df.copy()
                     for col in ['counters', 'position']:
                        if col in output_df.columns:
                             output_df[col] = output_df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
                     
                     if 'matchups' in output_df.columns:
                          output_df['matchups'] = output_df['matchups'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
                     
                     self.conn.update(worksheet=version_name, data=output_df)
                     st.cache_data.clear() # Clear cache so next load gets the clean sheet
                 except Exception as e:
                     print(f"Auto-fix IDs save failed: {e}") # Log but don't crash app

            return df
        except Exception as e:
            # st.error(f"Error loading heroes from {version_name}: {e}")
            return pd.DataFrame()

    def load_matchups(self, hero_name, version_name):
        """
        Loads matchups for a specific hero from the 'matchups' worksheet, filtered by version.
        """
        try:
            try:
                df = self.conn.read(worksheet="matchups")
            except:
                return []
            
            if df.empty or 'hero' not in df.columns or 'version' not in df.columns:
                return []
            
            # Filter by Hero AND Version
            matches = df[
                (df['hero'] == hero_name) & 
                (df['version'] == version_name)
            ].to_dict('records')
            
            return matches
        except Exception as e:
            # st.error(f"Error loading matchups: {e}") # Silent fail or log
            return []

    def add_matchup(self, hero_name, lane, opponent_name, win_rate, version_name):
        """
        Adds a bi-directional matchup to the 'matchups' sheet for a specific version.
        """
        try:
            try:
                df = self.conn.read(worksheet="matchups")
            except:
                # Create empty DF if sheet doesn't exist
                df = pd.DataFrame(columns=['hero', 'lane', 'opponent', 'win_rate', 'version'])

            # Ensure columns
            required_cols = ['hero', 'lane', 'opponent', 'win_rate', 'version']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = "" # Add missing cols

            # Prepare new rows
            row1 = {"hero": hero_name, "lane": lane, "opponent": opponent_name, "win_rate": win_rate, "version": version_name}
            
            # Reverse logic
            rev_wr = 100 - int(win_rate)
            row2 = {"hero": opponent_name, "lane": lane, "opponent": hero_name, "win_rate": rev_wr, "version": version_name}
            
            # DELETE collisions first (Update behavior) for THIS VERSION
            c1 = (df['hero'] == hero_name) & (df['opponent'] == opponent_name) & (df['lane'] == lane) & (df['version'] == version_name)
            c2 = (df['hero'] == opponent_name) & (df['opponent'] == hero_name) & (df['lane'] == lane) & (df['version'] == version_name)
            
            df = df[~(c1 | c2)]
            
            # Append new
            new_rows = pd.DataFrame([row1, row2])
            df = pd.concat([df, new_rows], ignore_index=True)
            
            self.conn.update(worksheet="matchups", data=df)
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Error adding matchup: {e}")
            return False

    def delete_matchup(self, hero_name, lane, opponent_name, version_name):
        """
        Deletes a matchup (and its reverse) from the sheet for a specific version.
        """
        try:
            try:
                df = self.conn.read(worksheet="matchups")
            except:
                return False
            
            if df.empty: return True
            if 'version' not in df.columns: return True # If no version col match, nothing to delete for specific version?

            # Condition 1: hero=A, opp=B, ver=V
            c1 = (df['hero'] == hero_name) & (df['opponent'] == opponent_name) & (df['lane'] == lane) & (df['version'] == version_name)
            # Condition 2: hero=B, opp=A, ver=V
            c2 = (df['hero'] == opponent_name) & (df['opponent'] == hero_name) & (df['lane'] == lane) & (df['version'] == version_name)
            
            df = df[~(c1 | c2)]
            
            self.conn.update(worksheet="matchups", data=df)
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Error deleting matchup: {e}")
            return False

    # ------------------------------------------------------------------
    # PLAYER MANAGEMENT
    # ------------------------------------------------------------------
    def get_all_players(self):
        try:
            try:
                df = self.conn.read(worksheet="players")
            except:
                 return pd.DataFrame(columns=['id', 'ign', 'positions'])
            
            if df.empty: return pd.DataFrame(columns=['id', 'ign', 'positions'])
            return df
        except Exception as e:
            st.error(f"Error loading players: {e}")
            return pd.DataFrame()

    def create_player(self, ign, positions):
        try:
            df = self.get_all_players()
            
            # Check for duplicate IGN? (Optional but good)
            if 'ign' in df.columns and ign in df['ign'].values:
                return False, "Player IGN already exists!"

            new_id = str(uuid.uuid4())
            # Join positions to string for storage
            pos_str = ", ".join(positions) if isinstance(positions, list) else positions
            
            new_row = pd.DataFrame([{
                "id": new_id, 
                "ign": ign, 
                "positions": pos_str
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            self.conn.update(worksheet="players", data=df)
            st.cache_data.clear()
            return True, "Player created successfully!"
        except Exception as e:
            return False, str(e)

    # ------------------------------------------------------------------
    # TEAM MANAGEMENT
    # ------------------------------------------------------------------
    def get_all_teams(self):
        try:
            try:
                df = self.conn.read(worksheet="teams")
            except:
                return pd.DataFrame(columns=['id', 'team_name', 'logo_url', 'roster'])
            return df
        except:
             return pd.DataFrame()

    def create_team(self, team_name, logo_url, roster_data=None):
        """
        Creates a new team. 
        roster_data: dict, optional. If None, initializes empty structure.
        """
        try:
            try:
                df = self.conn.read(worksheet="teams")
            except:
                df = pd.DataFrame(columns=['id', 'team_name', 'logo_url', 'roster'])
            
            # Ensure columns exist
            for col in ['id', 'team_name', 'logo_url', 'roster']:
                if col not in df.columns: df[col] = ""

            new_id = str(uuid.uuid4())
            
            if roster_data is None:
                roster_data = {"main": {}, "sub": [], "coach": None}
                
            roster_json = json.dumps(roster_data)
            
            new_row = pd.DataFrame([{
                "id": new_id,
                "team_name": team_name,
                "logo_url": logo_url,
                "roster": roster_json
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            self.conn.update(worksheet="teams", data=df)
            st.cache_data.clear()
            return True, "Team created successfully!"
        except Exception as e:
            return False, str(e)

    def update_team(self, team_id, updated_data):
        """
        Updates an existing team.
        updated_data: dict of fields to update (e.g. roster, team_name)
        """
        try:
            try:
                df = self.conn.read(worksheet="teams")
            except:
                return False, "Teams sheet not found."
            
            if df.empty: return False, "No teams found."
            
            if 'id' not in df.columns:
                 return False, "ID column missing."

            # Find row index
            idx = df[df['id'] == team_id].index
            if len(idx) == 0:
                return False, "Team ID not found."
            
            idx = idx[0]
            
            # Update fields
            for k, v in updated_data.items():
                if k == 'roster' and isinstance(v, (dict, list)):
                    v = json.dumps(v)
                
                if k in df.columns:
                    df.at[idx, k] = v
            
            self.conn.update(worksheet="teams", data=df)
            st.cache_data.clear()
            return True, "Team updated successfully!"
        except Exception as e:
            return False, str(e)

    # ------------------------------------------------------------------
    # DRAFT LOGGING
    # ------------------------------------------------------------------
    def log_draft(self, mode, blue_team, red_team, blue_bans, red_bans, prediction):
        try:
            try:
                df = self.conn.read(worksheet="draft_logs")
            except:
                df = pd.DataFrame(columns=['timestamp', 'mode', 'blue_team', 'red_team', 'blue_bans', 'red_bans', 'winner_prediction'])
            
            # Ensure columns
            for col in ['timestamp', 'mode', 'blue_team', 'red_team', 'blue_bans', 'red_bans', 'winner_prediction']:
                if col not in df.columns: df[col] = ""

            new_row = pd.DataFrame([{
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "mode": mode,
                "blue_team": json.dumps(blue_team),
                "red_team": json.dumps(red_team),
                "blue_bans": json.dumps(blue_bans),
                "red_bans": json.dumps(red_bans),
                "winner_prediction": prediction
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            self.conn.update(worksheet="draft_logs", data=df)
            return True, "Draft logged successfully!"
        except Exception as e:
            return False, str(e)

    def save_hero(self, hero_data, version_name="VERSION 1.60.1.10"):
        """
        Add or Update a hero (Attributes ONLY).
        Matchups are now handled externally in 'matchups' sheet.
        """
        try:
            df = self.load_heroes(version_name)
            
            # Helper to ensure unique ID
            if 'id' not in hero_data or not hero_data['id']:
                hero_data['id'] = str(uuid.uuid4())
            
            # --- Update/Add Primary Hero ---
            save_data = hero_data.copy()
            
            # Remove 'matchups' key if present, we don't save it to main sheet anymore
            if 'matchups' in save_data:
                del save_data['matchups']

            # Check existence
            if 'id' in df.columns and save_data['id'] in df['id'].values:
                idx = df[df['id'] == save_data['id']].index[0]
                for k, v in save_data.items():
                    if k in df.columns:
                        df.at[idx, k] = v
            else:
                new_row = pd.DataFrame([save_data])
                df = pd.concat([df, new_row], ignore_index=True)
            
            # --- Serialize & Save ---
            output_df = df.copy()
            for col in ['counters', 'position']:
                if col in output_df.columns:
                     output_df[col] = output_df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
            
            # Remove matchups col from output if it lingers?
            # It might exist in old schema. We can leave it or ignore it.
            # safe to verify 'matchups' is NOT in the columns we care about, or just leave it alone.

            self.conn.update(worksheet=version_name, data=output_df)
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Error saving hero: {e}")
            return False

    def delete_hero(self, hero_id, version_name="VERSION 1.60.1.10"):
        try:
            df = self.load_heroes(version_name)
            if 'id' in df.columns:
                df = df[df['id'] != hero_id]
                
                # Convert lists to strings for writing
                output_df = df.copy()
                for col in ['counters', 'position']:
                     if col in output_df.columns:
                        output_df[col] = output_df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
                
                if 'matchups' in output_df.columns:
                     output_df['matchups'] = output_df['matchups'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
                        
                self.conn.update(worksheet=version_name, data=output_df)
                st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Error deleting hero: {e}")
            return False

# INITIALIZE DB
db = DBManager()

# ==============================================================================
# DIALOGS
# ==============================================================================



def render_hero_editor_ui():
    """
    Full-page Hero Editor.
    Reads hero data from st.session_state['editing_hero'].
    """
    hero = st.session_state.get('editing_hero')
    if not hero:
        st.error("No hero selected for editing.")
        if st.button("Back to Grid"):
            st.session_state['show_editor'] = False
            st.rerun()
        return

    # Header with Back Button
    c_back, c_title = st.columns([1, 5])
    with c_back:
        if st.button("⬅️ Back"):
            st.session_state['show_editor'] = False
            st.session_state.pop('editing_hero', None)
            st.rerun()
    with c_title:
        st.title(f"Edit Hero: {hero.get('name')}")

    current_version = st.session_state.get('current_version', 'Sheet1')
    
    # Fetch current heroes for Counters
    current_heroes_df = db.load_heroes(current_version)
    all_hero_names = sorted(current_heroes_df['name'].dropna().unique().tolist()) if not current_heroes_df.empty else []

    def safe_get_index(options, value, default_index=0):
        if value and str(value) in options:
            return options.index(str(value))
        return default_index
    
    # --- FORM INPUTS ---
    c1, c2 = st.columns(2)
    with c1:
        h_name = st.text_input("Hero Name", value=hero.get('name', ''))
        
        tier_opts = ["SS", "S", "A", "B", "C"]
        tier_idx = safe_get_index(tier_opts, hero.get('tier'), 3)
        h_tier = st.selectbox("Tier", tier_opts, index=tier_idx)
        
        class_opts = ["Fighter", "Assassin", "Mage", "Carry", "Support", "Tank"]
        current_class = hero.get('class', [])
        # Normalize class input to list
        if isinstance(current_class, str): 
            current_class = [c.strip() for c in current_class.split(',')] if ',' in current_class else [current_class] if current_class else []
        elif not isinstance(current_class, list):
            current_class = []
        
        # Ensure defaults are valid
        default_classes = [c for c in current_class if c in class_opts]
        h_class = st.multiselect("Class", class_opts, default=default_classes)
    
    with c2:
        pos_opts = ['Dark Slayer', 'Jungle', 'Mid', 'Abyssal', 'Roam']
        current_pos = hero.get('position', [])
        # Normalize position input to list
        if isinstance(current_pos, str): 
            current_pos = [p.strip() for p in current_pos.split(',')] if ',' in current_pos else [current_pos] if current_pos else []
        elif not isinstance(current_pos, list):
            current_pos = []

        h_pos = st.multiselect("Position", pos_opts, default=[p for p in current_pos if p in pos_opts])
        
        time_opts = ["Early Game", "Late Game", "Balanced"]
        h_timing = st.selectbox("Power Spike", time_opts, index=safe_get_index(time_opts, hero.get('timing'), 2))
        
        current_counters = hero.get('counters', [])
        if isinstance(current_counters, str):
            current_counters = [c.strip() for c in current_counters.split(',')] if ',' in current_counters else [current_counters] if current_counters else []
        elif not isinstance(current_counters, list):
            current_counters = []

        h_counters = st.multiselect("Weak Against", all_hero_names, default=[c for c in current_counters if c in all_hero_names])
        
    st.markdown("---")
    
    # --- Lane Matchups ---
    st.subheader("🎯 Lane Matchups")
    
    # Internal state for matchups (Load from DB)
    if 'matchups_loaded_for' not in st.session_state or st.session_state['matchups_loaded_for'] != hero.get('name'):
         st.session_state['temp_matchups'] = db.load_matchups(hero.get('name'), current_version)
         st.session_state['matchups_loaded_for'] = hero.get('name')

    # Display List
    if st.session_state['temp_matchups']:
        st.caption("Current Matchups:")
        for idx, m in enumerate(st.session_state['temp_matchups']):
            c_info, c_edit, c_del = st.columns([5, 1, 1])
            with c_info:
                lane_str = f"[{m.get('lane', 'Any')}]"
                st.markdown(f"**{lane_str}** vs **{m['opponent']}** : `{m['win_rate']}%`")
            with c_edit:
                if st.button("✏️", key=f"edit_m_{idx}"):
                    st.session_state['edit_matchup_idx'] = idx
                    st.session_state['edit_lane'] = m.get('lane')
                    st.session_state['edit_opponent'] = m.get('opponent')
                    st.session_state['edit_win_rate'] = int(m.get('win_rate', 50))
                    st.rerun()
            with c_del:
                if st.button("🗑️", key=f"del_m_{idx}"):
                    # DELETE from DB
                    if db.delete_matchup(hero.get('name'), m.get('lane'), m.get('opponent'), current_version):
                        st.success("Deleted!")
                        st.session_state.pop('matchups_loaded_for', None) # Force reload
                        st.rerun()
    else:
        st.info("No matchups recorded.")

    # Determine Edit Mode
    edit_idx = st.session_state.get('edit_matchup_idx', None)
    is_editing = edit_idx is not None
    
    form_label = f"✏️ แก้ไขข้อมูล (Edit Matchup #{edit_idx+1})" if is_editing else "➕ เพิ่มข้อมูลการชนเลน (Add New Matchup)"
    btn_label = "Update Matchup" if is_editing else "Confirm Add"

    # Add/Edit Matchup Form (Expander)
    should_expand = is_editing 
    
    with st.expander(form_label, expanded=should_expand):
        with st.form("add_matchup_form"):
            ac1, ac2 = st.columns(2)
            
            # Pre-fill
            my_positions = h_pos if h_pos else ["Mid", "Roam", "Abyssal", "Dark Slayer", "Jungle"]
            d_lane = st.session_state.get('edit_lane') if is_editing else None
            try:
                lane_ix = my_positions.index(d_lane) if d_lane in my_positions else 0
            except:
                lane_ix = 0
            
            with ac1:
                new_m_lane = st.selectbox("My Lane", my_positions, index=lane_ix)

            opps = [n for n in all_hero_names if n != hero.get('name')]
            d_opp = st.session_state.get('edit_opponent') if is_editing else None
            try:
                opp_ix = opps.index(d_opp) if d_opp in opps else 0
            except:
                opp_ix = 0
            
            with ac2:
                new_m_opp = st.selectbox("Opponent", opps, index=opp_ix)
            
            d_wr = st.session_state.get('edit_win_rate', 50) if is_editing else 50
            new_m_wr = st.slider("Win Rate %", 0, 100, d_wr)
            
            c_submit, c_cancel = st.columns([1, 1])
            with c_submit:
                submitted = st.form_submit_button(btn_label)
            with c_cancel:
                canceled = st.form_submit_button("Cancel") 
            
            if canceled:
                st.session_state.pop('edit_matchup_idx', None)
                st.session_state.pop('edit_lane', None)
                st.session_state.pop('edit_opponent', None)
                st.session_state.pop('edit_win_rate', None)
                st.rerun()

            if submitted:
                # DB OPERATION
                # Bi-directional Add/Update
                if db.add_matchup(hero.get('name'), new_m_lane, new_m_opp, new_m_wr, current_version):
                     st.success("Matchup Saved!")
                     # Clear Edit State
                     st.session_state.pop('edit_matchup_idx', None)
                     st.session_state.pop('edit_lane', None)
                     st.session_state.pop('edit_opponent', None)
                     st.session_state.pop('edit_win_rate', None)
                     # Force reload to see changes
                     st.session_state.pop('matchups_loaded_for', None) 
                     st.rerun()
                else:
                    st.error("Failed to save matchup.")

    st.markdown("---")
    
    # --- UNSAVED CHANGES DETECTION ---
    has_changes = False
    
    # 1. Compare Normalized Values
    c_name = hero.get('name', '')
    if h_name != c_name: has_changes = True
    
    c_tier = hero.get('tier', '')
    if h_tier != c_tier: has_changes = True
    
    # Lists (Sort for comparison)
    if set(h_class) != set(default_classes): has_changes = True
    if set(h_pos) != set(current_pos): has_changes = True
    
    c_timing = hero.get('timing', '')
    if h_timing != c_timing: has_changes = True
    
    if set(h_counters) != set(current_counters): has_changes = True

    # Note: Matchups are saved instantly, so we don't track them as "unsaved" in this context context,
    # as the user requested "existing logic for saving ... intact".
    
    col_save, col_del = st.columns([3, 1])
    with col_save:
        if has_changes:
            st.warning("⚠️ คุณมีการแก้ไขข้อมูลที่ยังไม่ได้บันทึก")
            
        if st.button("💾 บันทึกการแก้ไข", type="primary", use_container_width=True, help="Save changes to Google Sheets"):
            updated_data = {
                "id": hero.get('id'),
                "name": h_name,
                "tier": h_tier,
                "class": ", ".join(h_class) if isinstance(h_class, list) else h_class,
                "position": h_pos,
                "timing": h_timing,
                "counters": h_counters,
                # Matchups handled separately now
            }
            
            if db.save_hero(updated_data, current_version):
                st.success(f"Hero {h_name} updated!")
                time.sleep(1)
                st.session_state['show_editor'] = False # Go back to grid
                st.rerun()
    
    with col_del:
        # Add some vertical spacing or align with the bottom
        st.write("") 
        if st.button("🗑️ Delete Hero", use_container_width=True):
            if db.delete_hero(hero.get('id'), current_version):
                st.warning(f"Hero {h_name} deleted!")
                time.sleep(1)
                st.session_state['show_editor'] = False # Go back to grid
                st.rerun()

@st.dialog("🦸 Add New Hero")
def add_hero_dialog():
    current_version = st.session_state.get('current_version', 'Sheet1')
    
    current_heroes_df = db.load_heroes(current_version)
    all_hero_names = sorted(current_heroes_df['name'].dropna().unique().tolist()) if not current_heroes_df.empty else []

    with st.form("f_add_hero"):
        c1, c2 = st.columns(2)
        with c1:
            h_name = st.text_input("Hero Name", placeholder="e.g. Valhein")
            h_tier = st.selectbox("Tier", ["SS", "S", "A", "B", "C"])
            h_role = st.selectbox("Class", ["Assassin", "Mage", "Fighter", "Carry", "Tank", "Support"])
        
        with c2:
            h_pos = st.multiselect("Position", ["Jungle", "Mid", "Abyssal", "Dark Slayer", "Roam"])
            h_time = st.selectbox("Power Spike", ["Early Game", "Late Game", "Balanced"])
            h_counters = st.multiselect("Weak Against", all_hero_names)
            
        st.markdown("---")
        
        if st.form_submit_button("🔥 Register Hero"):
            if not h_name:
                st.error("Hero Name is required!")
            else:
                hero_data = {
                    "name": h_name,
                    "tier": h_tier,
                    "class": h_role,
                    "position": h_pos,
                    "timing": h_time,
                    "counters": h_counters,
                    # ID is handled in save_hero
                }
                
                if db.save_hero(hero_data, current_version):
                    st.success(f"Hero {h_name} added to {current_version}!")
                    time.sleep(1)
                    st.rerun()

# ==============================================================================
# UI COMPONENTS
# ==============================================================================

def render_hero_grid(heroes):
    """
    Render a grid of heroes as clickable cards.
    Each card is a button that opens the edit dialog.
    """
    cols = st.columns(4) # 4 cards per row for better visibility on wide screens
    
    for i, hero in enumerate(heroes):
        with cols[i % 4]:
            # Data Fallbacks
            name = hero.get('name', 'UNKNOWN')
            tier = hero.get('tier', '?')
            role = hero.get('class', '-')
            
            # Ensure lists are strings if accessing directly
            pos_list = hero.get('position', [])
            pos_str = ", ".join(pos_list) if isinstance(pos_list, list) else str(pos_list)
            
            timing = hero.get('timing', '-')
            ct_list = hero.get('counters', [])
            
            # Format Counter list for display (limit to 2)
            if ct_list:
                ct_display = ", ".join(ct_list[:2])
                if len(ct_list) > 2:
                    ct_display += f" (+{len(ct_list)-2})"
            else:
                ct_display = "-"

            # --- HIGH FIDELITY CARD LABEL ---
            # Using Markdown colors for styling fields
            # Header: LARGE NAME ... [Tier] (Gold)
            
            # Tier: Gold/Yellow text
            tier_badge = f":orange[[{tier}]]" if tier else ""
            
            # --- MINIMALIST IMAGE CARD LABEL ---
            # Strategy: Use Markdown Image syntax to inject the image tag.
            # CSS will handle positioning it as absolute background.
            # Content: Image + Newlines + Name + Tier Badge
            
            img_url = hero.get('image_url', '')
            img_md = f"![bg]({img_url})" if img_url else ""
            
            # Tier Badge logic (using emoji or simple text)
            tier_badge = f"[{tier}]" if tier else ""
            
            # Using lots of newlines to push text down is handled by CSS flex-end, 
            # BUT we need content to exist.
            # Label = Image_MD + Name
            
            label = f"""{img_md}
            
{name} {tier_badge}"""
            
            # Render Button
            if st.button(label, key=f"card_{hero.get('id')}", use_container_width=True):
                 # Set state as requested
                 st.session_state['editing_hero'] = hero
                 st.session_state['show_editor'] = True
                 st.rerun()

def render_hero_grid_page(selected_ver_name):
    st.subheader(f"🦸 Hero Grid (Patch: {selected_ver_name})")
    
    # Controls & Filters
    c_search, c_filter = st.columns([2, 1])
    with c_search:
        search_query = st.text_input("🔍 Search Hero", placeholder="Type hero name...", label_visibility="collapsed")
    with c_filter:
        filter_pos = st.multiselect("Filter Position", options=['Dark Slayer', 'Jungle', 'Mid', 'Abyssal', 'Roam'], placeholder="All Positions", label_visibility="collapsed")

    # FAB Add Button
    col_add, _ = st.columns([1, 10])
    with col_add: 
        if st.button("＋", key="fab_add_hero", type="primary", help="Add New Hero"):
            add_hero_dialog()
    
    # Fetch Data
    df = db.load_heroes(selected_ver_name)
    
    filtered_heroes = []
    if not df.empty:
        all_heroes = df.to_dict('records')
        
        for hero in all_heroes:
            # Name Filter
            if search_query and search_query.lower() not in str(hero.get('name', '')).lower():
                continue
            
            # Position Filter
            if filter_pos:
                h_pos = hero.get('position', [])
                if not set(filter_pos).intersection(set(h_pos)):
                    continue
            
            filtered_heroes.append(hero)

        # Sort
        filtered_heroes.sort(key=lambda x: str(x.get('name', '')).strip().lower())

    if not filtered_heroes:
         if search_query or filter_pos:
             st.info(f"No heroes found matching filters.")
         else:
             st.info("No heroes found in this patch. Add one!")
    else:
        # Render the Grid
        render_hero_grid(filtered_heroes)

def render_version_control_ui():
    st.header("Version Control System")
    st.caption("Manage game patches using Google Sheets Tabs.")

    # 1. List current versions
    versions = db.get_all_versions()
    
    # 2. Create New Version Form
    st.subheader("Create New Patch")
    with st.form("new_patch_form"):
        new_v_name = st.text_input("New Version Name", placeholder="e.g. S1_Patch_2")
        
        # Options: Empty or Clone from existing
        clone_options = ["Empty"] + versions
        clone_source = st.selectbox("Clone Data From", clone_options)
        
        submitted = st.form_submit_button("Create Version")
        
        if submitted:
            if not new_v_name:
                st.error("Please enter a version name.")
            else:
                with st.spinner(f"Creating version '{new_v_name}'..."):
                    success = db.create_version(new_v_name, clone_source)
                    if success:
                        st.success(f"Successfully created version: {new_v_name}")
                        time.sleep(1.5)
                        st.rerun()
    
    st.markdown("---")
    st.subheader("Existing Versions")
    st.table(pd.DataFrame(versions, columns=["Available Versions"]))

# ==============================================================================
# PLAYER MANAGEMENT UI
# ==============================================================================

def render_player_manager():
    st.header("👤 Player Manager")
    
    t1, t2 = st.tabs(["Add Player", "All Players"])
    
    with t1:
        st.subheader("Register New Player")
        with st.form("add_player_form"):
            ign = st.text_input("IGN (In-Game Name)")
            
            role_options = ['Mid', 'Roam', 'Abyssal', 'Dark Slayer', 'Jungle', 'Coach']
            roles = st.multiselect("Positions", role_options)
            
            submitted = st.form_submit_button("Create Player")
            
            if submitted:
                if not ign or not roles:
                    st.error("Please fill in all fields.")
                else:
                    success, msg = db.create_player(ign, roles)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)

    with t2:
        st.subheader("Registered Players")
        players = db.get_all_players()
        if not players.empty:
            # Clean up display: Hide ID, Show IGN & Positions
            display_df = players[['ign', 'positions']].copy()
            display_df.columns = ["In-Game Name", "Positions"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No players registered yet.")

# ==============================================================================
# TEAM BUILDER UI
# ==============================================================================

def render_team_builder():
    st.header("🛡️ Team Builder")
    
    # 1. Determine View Mode
    team_id = st.session_state.get('editing_team_id', None)
    
    if team_id:
        render_team_roster_editor(team_id)
    else:
        render_team_grid_view()

def render_team_grid_view():
    st.subheader("Manage Teams")
    
    # Create Team Dialog
    @st.dialog("Create New Team")
    def create_team_dialog():
        with st.form("new_team_form"):
            t_name = st.text_input("Team Name")
            t_logo = st.text_input("Logo URL (Optional)")
            if st.form_submit_button("Create", type="primary"):
                if t_name:
                    success, msg = db.create_team(t_name, t_logo)
                    if success:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Name required.")

    if st.button("➕ Create New Team"):
        create_team_dialog()
        
    st.markdown("---")
    
    teams = db.get_all_teams()
    if teams.empty:
        st.info("No teams found. Create one to get started!")
        return

    # Render Teams as Cards
    cols = st.columns(3)
    for idx, row in teams.iterrows():
        c = cols[idx % 3]
        with c:
            with st.container(border=True):
                logo = row.get('logo_url')
                if isinstance(logo, str) and logo.strip().startswith("http"):
                    st.image(logo, width=50)
                else:
                    st.markdown("🛡️")
                
                st.subheader(row['team_name'])
                if st.button("Edit Roster", key=f"edit_team_{row['id']}"):
                    st.session_state['editing_team_id'] = row['id']
                    st.rerun()

def render_team_roster_editor(team_id):
    # Fetch Data
    teams = db.get_all_teams()
    if teams.empty: 
        st.error("Team not found.")
        return
        
    team = teams[teams['id'] == team_id].iloc[0]
    
    # Back Button
    if st.button("⬅️ Back to Teams"):
        st.session_state.pop('editing_team_id', None)
        st.rerun()

    c_head, c_img = st.columns([4, 1])
    with c_head:
        st.markdown(f"## Editing Roster: {team['team_name']}")
    with c_img:
        t_logo = team.get('logo_url')
        if isinstance(t_logo, str) and t_logo.strip().startswith("http"):
             st.image(t_logo, width=80)
        else:
             st.markdown("## 🛡️")

    # Parse Roster Data
    current_roster = json.loads(team['roster']) if team['roster'] else {"main": {}, "sub": [], "coach": None}
    
    # Fetch Players
    players_df = db.get_all_players()
    if players_df.empty: 
        st.warning("No players DB found.")
        return
        
    all_player_names = players_df['ign'].tolist()
    all_players_data = players_df.to_dict('records')
    # Map ID -> IGN for pre-filling
    id_to_name = dict(zip(players_df['id'], players_df['ign']))
    
    # Main Roles Form
    with st.form("edit_roster_form"):
        st.subheader("Starting Lineup")
        
        main_roles = ['Dark Slayer', 'Jungle', 'Mid', 'Abyssal', 'Roam']
        role_keys = {'Dark Slayer': 'ds', 'Jungle': 'jg', 'Mid': 'mid', 'Abyssal': 'adl', 'Roam': 'sup'}
        
        selected_main = {}
        cols = st.columns(5)
        
        for i, role in enumerate(main_roles):
            with cols[i]:
                # Filter Logic
                candidates = []
                for p in all_players_data:
                     # Robust position parsing
                    p_pos = p.get('positions', [])
                    if isinstance(p_pos, str): p_pos = [x.strip() for x in p_pos.split(',')]
                    elif not isinstance(p_pos, list): p_pos = []
                    
                    if role in p_pos:
                        candidates.append(p['ign'])
                
                # Pre-fill
                current_id = current_roster.get('main', {}).get(role_keys[role])
                current_name = id_to_name.get(current_id, "None")
                
                # Ensure current choice is in options
                options = ["None"] + candidates
                if current_name not in options and current_name != "None":
                     options.append(current_name)
                     
                idx = options.index(current_name) if current_name in options else 0
                selected_main[role] = st.selectbox(f"{role}", options, index=idx, key=f"e_{role}")

        st.markdown("---")
        st.subheader("Bench & Staff")
        c1, c2, c3 = st.columns(3)
        
        # Subs
        subs_ids = current_roster.get('sub', [])
        sub1_id = subs_ids[0] if len(subs_ids) > 0 else None
        sub2_id = subs_ids[1] if len(subs_ids) > 1 else None
        
        sub1_name = id_to_name.get(sub1_id, "None")
        sub2_name = id_to_name.get(sub2_id, "None")
        
        with c1:
            p_sub1 = st.selectbox("Sub 1", ["None"] + all_player_names, index=(["None"] + all_player_names).index(sub1_name) if sub1_name in all_player_names else 0)
        with c2:
            p_sub2 = st.selectbox("Sub 2", ["None"] + all_player_names, index=(["None"] + all_player_names).index(sub2_name) if sub2_name in all_player_names else 0)
            
        with c3:
            # Coach Logic
            coach_cands = []
            for p in all_players_data:
                p_pos = p.get('positions', [])
                if isinstance(p_pos, str): p_pos = [x.strip() for x in p_pos.split(',')]
                elif not isinstance(p_pos, list): p_pos = []
                
                if 'Coach' in p_pos: coach_cands.append(p['ign'])
            
            c_id = current_roster.get('coach')
            c_name = id_to_name.get(c_id, "None")
            
            c_opts = ["None"] + coach_cands
            if c_name not in c_opts and c_name != "None": c_opts.append(c_name)
            
            p_coach = st.selectbox("Coach", c_opts, index=c_opts.index(c_name) if c_name in c_opts else 0)

        if st.form_submit_button("💾 Save Roster", type="primary"):
            # Validation
            p_ds = selected_main['Dark Slayer']
            p_jg = selected_main['Jungle']
            p_mid = selected_main['Mid']
            p_adl = selected_main['Abyssal']
            p_sup = selected_main['Roam']
            
            sel = [p_ds, p_jg, p_mid, p_adl, p_sup, p_sub1, p_sub2, p_coach]
            real = [x for x in sel if x != "None"]
            if len(real) != len(set(real)):
                st.error("Duplicate players selected.")
                st.stop()
                
            # Payload construction
            name_to_id = dict(zip(players_df['ign'], players_df['id']))
            
            new_roster = {
                "main": {
                    "ds": name_to_id.get(p_ds),
                    "jg": name_to_id.get(p_jg),
                    "mid": name_to_id.get(p_mid),
                    "adl": name_to_id.get(p_adl),
                    "sup": name_to_id.get(p_sup)
                },
                "sub": [name_to_id.get(p_sub1), name_to_id.get(p_sub2)],
                "coach": name_to_id.get(p_coach)
            }
            
            success, msg = db.update_team(team_id, {"roster": new_roster})
            if success:
                st.success("Roster updated!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)

# ==============================================================================
# DRAFT ENGINE
# ==============================================================================
import random

class DraftEngine:
    def __init__(self, mode="HvB"):
        self.mode = mode # 'HvB', 'HvH', 'BvB'
        
        # Phases: 'INIT', 'BAN', 'PICK', 'COMPLETE'
        self.phase = 'BAN' 
        
        # Turn: 'BLUE' or 'RED'
        self.turn = 'BLUE'
        
        self.blue_bans = []
        self.red_bans = []
        self.blue_picks = []
        self.red_picks = []
        
        # Pro Tournament Sequence (18 Steps)
        # Phase 1: 4 Bans (2 each) -> 6 Picks (3 each)
        # Phase 2: 4 Bans (2 each) -> 4 Picks (2 each)
        # Format: (Phase, Side)
        self.sequence = [
            # --- PHASE 1 BANS ---
            ('BAN', 'BLUE'), ('BAN', 'RED'), ('BAN', 'BLUE'), ('BAN', 'RED'),
            # --- PHASE 1 PICKS ---
            ('PICK', 'BLUE'), ('PICK', 'RED'), ('PICK', 'RED'), ('PICK', 'BLUE'),
            ('PICK', 'BLUE'), ('PICK', 'RED'),
            # --- PHASE 2 BANS ---
            ('BAN', 'RED'), ('BAN', 'BLUE'), ('BAN', 'RED'), ('BAN', 'BLUE'),
            # --- PHASE 2 PICKS ---
            ('PICK', 'RED'), ('PICK', 'BLUE'), ('PICK', 'BLUE'), ('PICK', 'RED')
        ]
        self.step_index = 0
        self.draft_log = []

    def get_valid_heroes(self, all_heroes):
        # Exclude banned and picked
        taken = set(self.blue_bans + self.red_bans + self.blue_picks + self.red_picks)
        return [h for h in all_heroes if h not in taken]

    def is_complete(self):
        return self.step_index >= len(self.sequence)

    def get_current_state(self):
        if self.is_complete(): return 'COMPLETE', None
        return self.sequence[self.step_index]

    def make_move(self, hero_name):
        if self.is_complete(): return False
        
        phase, side = self.sequence[self.step_index]
        self.turn = side # Update turn indicator
        
        if phase == 'BAN':
            if side == 'BLUE': self.blue_bans.append(hero_name)
            else: self.red_bans.append(hero_name)
        else:
            if side == 'BLUE': self.blue_picks.append(hero_name)
            else: self.red_picks.append(hero_name)
            
        self.draft_log.append(f"{side} {phase}: {hero_name}")
        self.step_index += 1
        return True

    def auto_bot_move(self, all_heroes):
        # 1. Get Valid Candidates
        valid = self.get_valid_heroes(all_heroes)
        if not valid: return False
        
        # 2. Smart Logic (Placeholder for now: simple random)
        # In future: Check matchups, prioritize S-Tier, fill missing roles
        choice = random.choice(valid)
        
        return self.make_move(choice)

    def analyze_matchup(self):
        # Simple prediction based on nothing for now, placeholder
        return "50-50"

# Main Router (Placeholder)


# ==============================================================================
# DRAFT SIMULATOR UI
# ==============================================================================

def render_draft_simulator():
    st.header("🎮 Draft Simulator")
    
    # Fetch Data
    curr_ver = st.session_state.get('current_version', 'VERSION 1.60.1.10')
    heroes_df = db.load_heroes(curr_ver)
    if heroes_df.empty:
        st.warning("No heroes found for draft.")
        return
    all_hero_names = sorted(heroes_df['name'].dropna().unique().tolist())

    # Initialize Engine in Session State
    if 'draft_engine' not in st.session_state:
        st.session_state['draft_engine'] = None
    
    if st.session_state['draft_engine'] is None:
        # Configuration Screen
        st.subheader("Start New Draft")
        c1, c2, c3 = st.columns(3)
        if c1.button("� Human vs 🤖 Bot", use_container_width=True):
             st.session_state['draft_engine'] = DraftEngine("HvB")
             st.rerun()
        if c2.button("👤 Human vs 👤 Human", use_container_width=True):
             st.session_state['draft_engine'] = DraftEngine("HvH")
             st.rerun()
        if c3.button("🤖 Bot vs 🤖 Bot", use_container_width=True):
             st.session_state['draft_engine'] = DraftEngine("BvB")
             st.rerun()
        return

    # Engine Active
    engine = st.session_state['draft_engine']
    completed = engine.is_complete()
    
    # --- HEADER ---
    phase_text, side_text = engine.get_current_state()
    if completed:
        st.success(f"Draft Complete! Prediction: {engine.analyze_matchup()}")
        if st.button("Save & Reset"):
             db.log_draft(engine.mode, engine.blue_picks, engine.red_picks, engine.blue_bans, engine.red_bans, engine.analyze_matchup())
             st.session_state['draft_engine'] = None
             st.rerun()
    else:
        st.info(f"Phase: {phase_text} | Turn: {side_text}")

    # --- BOARD ---
    c_blue, c_mid, c_red = st.columns([2, 1, 2])
    
    with c_blue:
        st.markdown("### 🔵 Blue Team")
        # Bans
        st.caption("Bans: " + ", ".join(engine.blue_bans))
        for p in engine.blue_picks:
            st.button(p, key=f"blue_{p}", disabled=True, use_container_width=True)
            
    with c_red:
         st.markdown("### 🔴 Red Team")
         st.caption("Bans: " + ", ".join(engine.red_bans))
         for p in engine.red_picks:
            st.button(p, key=f"red_{p}", disabled=True, use_container_width=True)

    # --- ACTION AREA (HERO GRID) ---
    if not completed:
        st.markdown("---")
        
        # Phase Indicator
        p_color = "🔴" if side_text == 'RED' else "🔵"
        st.markdown(f"### {p_color} {side_text} TURN: **{phase_text}**")
        
        # Determine who is acting
        # HvB: If Turn=Blue -> Human. Turn=Red -> Bot.
        is_human_turn = False
        if engine.mode == "HvB":
            if engine.turn == 'BLUE': is_human_turn = True
        elif engine.mode == "HvH":
            is_human_turn = True
        # BvB: Always false
        
        if is_human_turn:
            st.caption("Select a hero to ban/pick:")
            
            # Search Bar
            search_q = st.text_input("🔍 Search Hero", placeholder="Type to filter...", label_visibility="collapsed")
            
            valid_heroes = engine.get_valid_heroes(all_hero_names)
            
            # Filter by Search
            if search_q:
                valid_heroes = [h for h in valid_heroes if search_q.lower() in h.lower()]
            
            if not valid_heroes:
                st.info("No heroes found.")
            else:
                cols = st.columns(6)
                for i, h in enumerate(valid_heroes):
                    if cols[i % 6].button(h, key=f"pick_{h}"):
                        engine.make_move(h)
                        st.rerun()
        else:
             # Bot Turn
             st.info(f"🤖 Bot ({side_text}) is thinking...")
             time.sleep(0.7)
             engine.auto_bot_move(all_hero_names)
             st.rerun()

# ==============================================================================
# MAIN PAGE ROUTER
# ==============================================================================

# Sidebar
with st.sidebar:
    st.markdown("# second-brain-core 🧠")
    
    # Refresh Button
    if st.button("🔄", type="primary", use_container_width=True, help="Refresh data from Google Sheets"):
        st.cache_data.clear()
        st.toast("Data refreshed from Google Sheets!", icon="✅")
        time.sleep(1)
        st.rerun()

    st.markdown("---")
    
    # Version Selector
    all_versions = db.get_all_versions()
    if not all_versions:
        # Fallback if no sheets exist/configured wrong
        all_versions = ["VERSION 1.60.1.10"]

    # Initialize Session State for Version
    if 'current_version' not in st.session_state:
        st.session_state['current_version'] = all_versions[0]
        
    # Ensure selected version is valid
    if st.session_state['current_version'] not in all_versions:
         st.session_state['current_version'] = all_versions[0]

    selected_ver = st.selectbox(
        "Current Patch", 
        all_versions, 
        index=all_versions.index(st.session_state['current_version'])
    )
    
    # Update state if changed
    if selected_ver != st.session_state['current_version']:
        st.session_state['current_version'] = selected_ver
        st.rerun()

    st.markdown("---")
    
    # --- SIDEBAR NAVIGATION ---
    st.markdown("### 🧭 Navigation")
    selected_page = st.radio(
        "Go to:", 
        ["Hero Database", "Player Manager", "Team Builder", "Draft Simulator", "Synergy Builder", "Version Control"],
        index=0
    )
    st.markdown("---")
    
    # Reset Editor State if leaving Hero Database
    if selected_page != "Hero Database":
         st.session_state['show_editor'] = False

# Main Content Router
try:
    if selected_page == "Hero Database":
        if st.session_state.get('show_editor', False):
             render_hero_editor_ui()
        else:
             render_hero_grid_page(st.session_state['current_version'])
             
    elif selected_page == "Player Manager":
        render_player_manager()
        
    elif selected_page == "Team Builder":
        render_team_builder()
    
    elif selected_page == "Draft Simulator":
        render_draft_simulator()
        
    elif selected_page == "Synergy Builder":
        st.header("Synergy Builder (Coming Soon)")
        st.info("Logic for Synergy Builder will be implemented here.")
        
    elif selected_page == "Version Control":
        render_version_control_ui()
        
except Exception as e:
    st.error(f"Application Error: {e}")
    st.exception(e)
