import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import cloudinary
import cloudinary.uploader
from datetime import datetime
import time

# ==============================================================================
# CONFIG & STYLE
# ==============================================================================
st.set_page_config(
    page_title="TAOX Brain - ROV Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Esports Vibe (Dark + Gold/Black + Red Alerts)
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 20, 0.6);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); /* Neon Glow */
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* Subheadings */
    .dashboard-subheader {
        color: #00f2ff; /* Cyan */
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        text-transform: uppercase;
        text-shadow: 0 0 5px rgba(0, 242, 255, 0.3);
    }

    /* Buttons (Glass Shards) */
    .stButton > button {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.6);
        transform: scale(1.02);
    }

    /* Inputs & Selects (Glass) */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stMultiSelect > div > div > div, .stNumberInput > div > div > input, .stTextArea > div > textarea {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 6px;
    }
    
    /* Glass Card Class */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* Highlight Text */
    .highlight {
        color: #00f2ff;
        font-weight: bold;
    }
    
    /* Metric Value */
    [data-testid="stMetricValue"] {
        color: #00f2ff !important;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.4);
    }
    
    /* Table/DataFrame */
    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BACKEND INITIALIZATION (SAFE MODE)
# ==============================================================================

@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except:
        return None

@st.cache_resource
def init_cloudinary():
    try:
        c_config = st.secrets["cloudinary"]
        cloudinary.config(
            cloud_name=c_config["cloud_name"],
            api_key=c_config["api_key"],
            api_secret=c_config["api_secret"]
        )
        return True
    except:
        return False

# Attempt connections
db = init_firebase()
cloud_ready = init_cloudinary()

# Check for secrets existence to display the specific visual warning requested
secrets_found = False
try:
    if "firebase" in st.secrets:
        secrets_found = True
except FileNotFoundError:
    secrets_found = False
except Exception:
    secrets_found = False

# ==============================================================================
# DATA HELPERS
# ==============================================================================

def get_heroes_df():
    heroes_ref = db.collection("heroes")
    docs = heroes_ref.stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        data.append(d)
    if not data:
        return pd.DataFrame(columns=["id", "name", "role", "tier", "meta_score", "image_url", "counters", "weak_against", "taox_note"])
    return pd.DataFrame(data)

def get_combos():
    if not db:
        return []
    docs = db.collection('combos').stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def check_active_combos(current_team_list, all_combos):
    active = []
    current_ids = {h['id'] for h in current_team_list}
    for combo in all_combos:
        combo_ids = set(combo.get('hero_ids', []))
        if combo_ids and combo_ids.issubset(current_ids):
            active.append(combo)
    return active

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("# TAOX BRAIN 🧠")
    st.markdown("**ROV Analyst System**")
    st.markdown("---")
    
    menu = st.radio(
        "Navigation", 
        ["Overview", "Hero CMS", "Combo Manager", "Draft Arena", "Scrim Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### System Status:")
    
    # Status Indicators
    db_status = "🟢 Online" if db else "🔴 Offline"
    cloud_status = "🟢 Online" if cloud_ready else "🔴 Offline"
    
    # Use formatted markdown for color
    if db:
         st.markdown(f"- Database: <span class='status-online'>Online</span>", unsafe_allow_html=True)
    else:
         st.markdown(f"- Database: <span class='status-offline'>Offline</span>", unsafe_allow_html=True)
         
    if cloud_ready:
         st.markdown(f"- Media Cloud: <span class='status-online'>Online</span>", unsafe_allow_html=True)
    else:
         st.markdown(f"- Media Cloud: <span class='status-offline'>Offline</span>", unsafe_allow_html=True)

# ==============================================================================
# MAIN CONTENT
# ==============================================================================

if menu == "Overview":
    # 1. Error Handling Display (Requested specific visual)
    if not secrets_found:
        st.error(r"No secrets found. Valid paths for a secrets.toml file are: C:\Users\Suppa\.streamlit\secrets.toml, C:\Users\Suppa\TAOX Brain\.streamlit\secrets.toml")
        st.error(r"No secrets found. Valid paths for a secrets.toml file are: C:\Users\Suppa\.streamlit\secrets.toml, C:\Users\Suppa\TAOX Brain\.streamlit\secrets.toml")

    # 2. Welcome Header
    st.title("WELCOME BACK, TAOX.")
    
    # 3. Dashboard Section
    st.markdown('<div class="dashboard-subheader">DASHBOARD</div>', unsafe_allow_html=True)
    
    # 4. Feature List (Glass Card)
    st.markdown("""
    <div class="glass-card">
        <ul>
            <li><span class="highlight">Hero Knowledge</span>: Update meta scores and counter strategies.</li>
            <li><span class="highlight">Draft Arena</span>: Simulate drafts against the 'Red Team' bot.</li>
            <li><span class="highlight">Analytics</span>: Upload scrim results and track win rates.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

elif menu == "Hero CMS":
    st.title("HERO CMS")
    
    if not db:
        st.error("Database not connected. Please check secrets.")
    else:
        # 1. Fetch Data
        heroes_ref = db.collection('heroes')
        docs = heroes_ref.stream()
        heroes_data = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            heroes_data.append(d)
            
        # 2. Check for Empty State
        if not heroes_data:
            st.info("The Knowledge Base is currently empty.")
            
            # 3. Initialize Button
            if st.button("🚀 Initialize Dummy Data (Starter Pack)"):
                starter_heroes = [
                    {"name": "Nakroth", "role": "Assassin", "tier": "S", "meta_score": 95, "counters": ["aleister", "arum"], "img": "", "taox_note": "Farm fast, split push."},
                    {"name": "Aya", "role": "Support", "tier": "S", "meta_score": 99, "counters": ["zip", "taara"], "img": "", "taox_note": "Stick to the tank/carry."},
                    {"name": "Florentino", "role": "Fighter", "tier": "A", "meta_score": 92, "counters": ["arum", "aleister"], "img": "", "taox_note": "Skill dependent."},
                    {"name": "Krixi", "role": "Mage", "tier": "A", "meta_score": 85, "counters": ["nakroth"], "img": "", "taox_note": "Easy burst damage."},
                    {"name": "Zip", "role": "Support", "tier": "S", "meta_score": 98, "counters": ["mina"], "img": "", "taox_note": "Save teammates."}
                ]
                
                progress_bar = st.progress(0)
                for i, hero in enumerate(starter_heroes):
                    db.collection('heroes').add(hero)
                    progress_bar.progress((i + 1) / len(starter_heroes))
                    time.sleep(0.1) # Visual effect
                
                st.success("Starter Pack Initialized! Reloading...")
                time.sleep(1)
                st.rerun()
                
        # 4. Data Exists - Show Editor
        else:
            df = pd.DataFrame(heroes_data)
            
            # Configure columns
            # Ensure columns exist even if some docs miss them
            desired_cols = ["name", "role", "tier", "meta_score", "taox_note", "counters", "img", "id"]
            for c in desired_cols:
                if c not in df.columns:
                    df[c] = ""
            
            st.markdown(f"### Managed Heroes ({len(df)})")
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "id": None, # Hide ID
                    "img": st.column_config.ImageColumn("Image", width="small"),
                    "tier": st.column_config.SelectboxColumn("Tier", options=["S", "A", "B", "C"], required=True),
                    "meta_score": st.column_config.ProgressColumn("Meta Score", min_value=0, max_value=100, format="%d"),
                    "taox_note": st.column_config.TextColumn("Taox Note", width="large"),
                    "role": st.column_config.SelectboxColumn("Role", options=["Assassin", "Mage", "Fighter", "Support", "Tank", "Carry"]),
                },
                use_container_width=True,
                num_rows="dynamic",
                key="hero_editor"
            )
            
            if st.button("💾 Save Changes to Cloud"):
                # Handle Updates & New Rows
                # Note: st.data_editor returns a new DF. We need to detect changes.
                # For simplicity in this prompt's context, we iterate and upsert.
                # Optimized approach: Only update what changed.
                # 'id' logic: Existing rows have IDs. New rows (added via UI) might have NaN or None in 'id'.
                
                with st.spinner("Syncing to Firestore..."):
                    for index, row in edited_df.iterrows():
                        hero_data = row.to_dict()
                        hero_id = hero_data.pop("id", None) # Remove ID from data payload
                        
                        # Clean data (handle NaN, etc if needed)
                        # Ensure meta_score is int
                        try:
                            hero_data["meta_score"] = int(hero_data["meta_score"])
                        except:
                            hero_data["meta_score"] = 0
                            
                        if hero_id and isinstance(hero_id, str) and len(hero_id) > 1:
                            # Update existing
                            db.collection('heroes').document(hero_id).set(hero_data, merge=True)
                        else:
                            # Create new
                            # If row was deleted? st.data_editor handles current state. 
                            # Deletions from DB require tracking deleted rows, which st.data_editor doesn't provide directly easily without session state tracking of original.
                            # For now, we assume 'Add/Edit'. Deletion logic requires more complex setup (comparing original vs new IDs).
                            if pd.notna(row['name']) and row['name'] != "":
                                db.collection('heroes').add(hero_data)
                    
                    st.success("Knowledge Base Updated!")
                    time.sleep(1)
                    st.rerun()

elif menu == "Combo Manager":
    st.title("COMBO MANAGER ⚡")
    
    if not db:
        st.error("Database required.")
    else:
        heroes_df = get_heroes_df()
        
        # --- Create Combo ---
        with st.expander("Create New Synergy", expanded=True):
            with st.form("new_combo"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    # Multiselect needs Names, map back to IDs
                    hero_names = heroes_df['name'].tolist()
                    selected_names = st.multiselect("Select Heroes (2-3)", hero_names, max_selections=3)
                    combo_name = st.text_input("Combo Name", placeholder="e.g. The Immortal Duo")
                with c2:
                    bonus = st.number_input("Bonus Score", min_value=0, value=10)
                    desc = st.text_area("Strategy Note")
                
                if st.form_submit_button("Save Synergy"):
                    if len(selected_names) < 2:
                        st.error("Select at least 2 heroes.")
                    elif not combo_name:
                        st.error("Name required.")
                    else:
                        # Map names to IDs
                        selected_ids = heroes_df[heroes_df['name'].isin(selected_names)]['id'].tolist()
                        
                        new_combo = {
                            "combo_name": combo_name,
                            "hero_ids": selected_ids,
                            "bonus_score": int(bonus),
                            "description": desc,
                            "created_at": datetime.now()
                        }
                        db.collection('combos').add(new_combo)
                        st.success(f"Added {combo_name}!")
                        time.sleep(1)
                        st.rerun()

        # --- List Combos ---
        st.subheader("Active Synergies")
        combos = get_combos()
        
        if not combos:
            st.info("No combos defined yet.")
        else:
            for c in combos:
                # Resolve Hero Names for display
                hero_ids = c.get('hero_ids', [])
                hero_names_display = heroes_df[heroes_df['id'].isin(hero_ids)]['name'].tolist()
                
                with st.container():
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"**{c.get('combo_name')}** (+{c.get('bonus_score')})")
                        st.caption(f"Heroes: {', '.join(hero_names_display)}")
                        st.caption(f"Note: {c.get('description')}")
                    with col_del:
                        if st.button("🗑️", key=f"del_{c['id']}"):
                            db.collection('combos').document(c['id']).delete()
                            st.rerun()
                    st.markdown("---")

elif menu == "Draft Arena":
    st.title("THE ARENA ⚔️")
    
    if not db:
        st.error("Database connection required for Draft Arena.")
    else:
        # --- 0. Data Fetching ---
        heroes_ref = db.collection('heroes')
        docs = heroes_ref.stream()
        hero_list = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            hero_list.append(d)
        heroes_df = pd.DataFrame(hero_list)
        
        if heroes_df.empty:
            st.warning("No heroes found. Please go to Hero CMS to initialize data.")
        else:
            # --- 1. Session State Management ---
            # Define Standard Draft Order (10 Steps for Sim)
            # steps: 0-3 Bans, 4-9 Picks. 
            # Sequence: B-Ban, R-Ban, B-Ban, R-Ban, B-Pick, R-Pick, R-Pick, B-Pick, B-Pick, R-Pick
            draft_order = [
                {"team": "Blue", "type": "BAN"},
                {"team": "Red", "type": "BAN"},
                {"team": "Blue", "type": "BAN"},
                {"team": "Red", "type": "BAN"},
                {"team": "Blue", "type": "PICK"},
                {"team": "Red", "type": "PICK"},
                {"team": "Red", "type": "PICK"},
                {"team": "Blue", "type": "PICK"},
                {"team": "Blue", "type": "PICK"},
                {"team": "Red", "type": "PICK"}
            ]

            if "turn_index" not in st.session_state:
                st.session_state.turn_index = 0
                st.session_state.blue_team = [] # list of hero dicts
                st.session_state.red_team = []
                st.session_state.bans = [] # list of hero dicts
                st.session_state.global_history = {'Blue': [], 'Red': []} # IDs of played heroes
                st.session_state.active_game_num = 1
                st.session_state.game_mode = "BO5"
                st.session_state.draft_active = False

            # --- 2. Game Settings (Pre-Game) ---
            if not st.session_state.draft_active:
                c1, c2 = st.columns(2)
                with c1:
                    st.session_state.game_mode = st.selectbox("Series Format", ["BO1", "BO3", "BO5", "BO7"], index=2)
                with c2:
                    st.write(f"Match Pending: Game {st.session_state.active_game_num}")
                    if st.button("START DRAFT"):
                        st.session_state.draft_active = True
                        st.session_state.turn_index = 0
                        st.session_state.blue_team = []
                        st.session_state.red_team = []
                        st.session_state.bans = []
                        st.rerun()
                
                # Reset Series
                if st.button("Reset Series History"):
                    st.session_state.global_history = {'Blue': [], 'Red': []}
                    st.session_state.active_game_num = 1
                    st.success("Series Reset.")

            else:
                # --- 3. Draft In Progress ---
                
                # Check End of Draft
                if st.session_state.turn_index >= len(draft_order):
                    st.success("Draft Complete!")
                    st.balloons()
                    
                    # Update History
                    blue_ids = [h['id'] for h in st.session_state.blue_team]
                    red_ids = [h['id'] for h in st.session_state.red_team]
                    
                    if st.button("Go to Next Game"):
                        st.session_state.global_history['Blue'].extend(blue_ids)
                        st.session_state.global_history['Red'].extend(red_ids)
                        st.session_state.active_game_num += 1
                        st.session_state.draft_active = False
                        st.session_state.turn_index = 0
                        st.session_state.blue_team = []
                        st.session_state.red_team = []
                        st.session_state.bans = []
                        st.rerun()
                    st.stop() # Stop rendering the rest

                # Current State Info
                current_step = draft_order[st.session_state.turn_index]
                current_team = current_step["team"]
                action_type = current_step["type"]
                
                # --- 4. Smart Bot Logic (Red Team) ---
                if current_team == "Red":
                    with st.spinner(f"🔴 Red Team is {action_type}ING..."):
                        time.sleep(1) # Sim thinking
                        
                        # AI Logic
                        # Filter available
                        used_ids = [h['id'] for h in st.session_state.blue_team + st.session_state.red_team + st.session_state.bans]
                        # Global Ban validation for Red? 
                        if st.session_state.game_mode == "BO7" and st.session_state.active_game_num < 7:
                            used_ids.extend(st.session_state.global_history['Red'])
                            
                        available = heroes_df[~heroes_df['id'].isin(used_ids)].copy()
                        # Ensure meta_score is int
                        available['meta_score'] = pd.to_numeric(available['meta_score'], errors='coerce').fillna(0)
                        
                        picked_hero = None
                        
                        if action_type == "BAN":
                            # Ban highest meta
                            if not available.empty:
                                picked_hero = available.sort_values("meta_score", ascending=False).iloc[0].to_dict()
                                st.session_state.bans.append(picked_hero)
                        
                        elif action_type == "PICK":
                            # Counter Logic
                            # Find if any available hero counters any Blue hero
                            # Logic: does available_hero['counters'] contain any BlueHero ID?
                            # Need to parse 'counters' (list)
                            
                            # Simple approach: Search for explicit counter in available pool
                            found_counter = False
                            
                            # Blue team IDs/Names
                            blue_names = [h['name'].lower() for h in st.session_state.blue_team]
                            
                            for idx, row in available.iterrows():
                                # Check row['counters']
                                c_list = row.get('counters', [])
                                if isinstance(c_list, list):
                                    # If any of the counters in c_list is in blue_names (fuzzy match)
                                    for c in c_list:
                                        if str(c).lower() in blue_names:
                                            picked_hero = row.to_dict()
                                            found_counter = True
                                            break
                                if found_counter:
                                    break
                            
                            if not found_counter and not available.empty:
                                # Fallback: Best Meta
                                picked_hero = available.sort_values("meta_score", ascending=False).iloc[0].to_dict()
                                
                            if picked_hero:
                                st.session_state.red_team.append(picked_hero)

                        # Advance Turn
                        st.session_state.turn_index += 1
                        st.rerun()

                # --- 5. UI (Top Section) ---
                st.markdown(f"### Game {st.session_state.active_game_num} | <span style='color:{'#1E90FF' if current_team=='Blue' else '#FF4500'}'>{current_team} Turn: {action_type}</span>", unsafe_allow_html=True)
                
                # --- SYNERGY CHECK ---
                all_combos = get_combos()
                active_synergies = check_active_combos(st.session_state.blue_team, all_combos)
                
                if active_synergies:
                    st.info(f"⚡ **ACTIVE SYNERGIES ({len(active_synergies)})**")
                    for s in active_synergies:
                        st.markdown(f"- **{s['combo_name']}** (+{s['bonus_score']}): {s['description']}")
                
                col_b, col_r = st.columns(2)
                with col_b:
                    st.info("🔵 BLUE TEAM")
                    cols = st.columns(5)
                    for i, h in enumerate(st.session_state.blue_team):
                        cols[i].image(h.get('img') or "https://via.placeholder.com/50", use_container_width=True)
                        cols[i].caption(h['name'])
                    
                with col_r:
                    st.error("🔴 RED TEAM")
                    cols = st.columns(5)
                    for i, h in enumerate(st.session_state.red_team):
                        cols[i].image(h.get('img') or "https://via.placeholder.com/50", use_container_width=True)
                        cols[i].caption(h['name'])

                st.markdown("---")
                st.write("🚫 **BANS:** " + ", ".join([h['name'] for h in st.session_state.bans]))

                # --- 6. Hero Grid (User Interaction) ---
                if current_team == "Blue":
                    st.subheader("Select Hero")
                    
                    # Filtering
                    role_filter = st.selectbox("Role", ["All", "Assassin", "Mage", "Fighter", "Support", "Tank", "Carry"])
                    
                    grid_df = heroes_df.copy()
                    if role_filter != "All":
                        grid_df = grid_df[grid_df['role'] == role_filter]
                    
                    # Determine Used Ids to Disable
                    used_ids = [h['id'] for h in st.session_state.blue_team + st.session_state.red_team + st.session_state.bans]
                    # Blue Global Ban check
                    if st.session_state.game_mode == "BO7" and st.session_state.active_game_num < 7:
                        used_ids.extend(st.session_state.global_history['Blue'])
                    
                    # Grid Layout
                    cols = st.columns(6)
                    for i, (idx, h) in enumerate(grid_df.iterrows()):
                        col = cols[i % 6]
                        is_disabled = h['id'] in used_ids
                        
                        label = h['name']
                        if h.get('tier') == 'S':
                            label += " 🔥"
                            
                        if col.button(label, key=h['id'], disabled=is_disabled, use_container_width=True):
                            # BLUE ACTION
                            if action_type == "BAN":
                                st.session_state.bans.append(h.to_dict())
                            elif action_type == "PICK":
                                st.session_state.blue_team.append(h.to_dict())
                            
                            st.session_state.turn_index += 1
                            st.rerun()

elif menu == "Scrim Analytics":
    st.title("SCRIM ANALYTICS 📈")
    
    if not db:
        st.error("Database connection required for Analytics.")
    else:
        # --- 1. File Uploader ---
        st.subheader("Upload Match Data")
        uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])
        
        if uploaded_file:
            try:
                df_upload = pd.read_excel(uploaded_file)
                # Validation? Let's assume user follows format for now or check cols
                required_cols = {"Date", "Hero", "Result", "Note"}
                if not required_cols.issubset(df_upload.columns):
                     st.error(f"Excel must contain columns: {required_cols}")
                else:
                    st.dataframe(df_upload.head())
                    if st.button("🚀 Upload to Cloud"):
                        with st.spinner("Uploading matches..."):
                            batch_count = 0
                            for _, row in df_upload.iterrows():
                                # Clean data
                                record = {
                                    "date": str(row["Date"]), # Ensure serializable
                                    "hero": str(row["Hero"]),
                                    "result": str(row["Result"]),
                                    "note": str(row["Note"]),
                                    "timestamp": datetime.now()
                                }
                                db.collection('matches').add(record)
                                batch_count += 1
                            st.success(f"Successfully uploaded {batch_count} matches!")
                            time.sleep(1)
                            st.rerun()
            except Exception as e:
                st.error(f"Error processing file: {e}")
                
        st.markdown("---")
        
        # --- 2. Dashboard ---
        st.subheader("Live Performance Dashboard")
        
        matches_ref = db.collection('matches')
        docs = matches_ref.stream()
        match_list = [d.to_dict() for d in docs]
        
        if not match_list:
            st.info("No match data found in cloud.")
        else:
            df_matches = pd.DataFrame(match_list)
            
            # --- KPIs ---
            total_matches = len(df_matches)
            # Normalize result string
            if 'result' in df_matches.columns:
                df_matches['result_norm'] = df_matches['result'].astype(str).str.lower().str.strip()
                total_wins = df_matches[df_matches['result_norm'].isin(['win', 'w', 'victory'])].shape[0]
            else:
                total_wins = 0
                
            win_rate = (total_wins / total_matches) * 100 if total_matches > 0 else 0
            
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Matches", total_matches)
            kpi2.metric("Total Wins", total_wins)
            kpi3.metric("Overall Win Rate", f"{win_rate:.1f}%")
            
            # --- Hero Performance ---
            st.markdown("#### Hero Performance")
            
            # Group by Hero
            # Ensure hero column exists and is clean
            if 'hero' in df_matches.columns:
                hero_stats = df_matches.groupby('hero').agg(
                    Pick_Count=('result', 'count'),
                    Wins=('result_norm', lambda x: x.isin(['win', 'w', 'victory']).sum())
                ).reset_index()
                
                hero_stats['Win Rate %'] = (hero_stats['Wins'] / hero_stats['Pick_Count']) * 100
                hero_stats = hero_stats.sort_values('Pick_Count', ascending=False)
                
                # Display Table
                st.dataframe(
                    hero_stats[['hero', 'Pick_Count', 'Win Rate %']],
                    use_container_width=True,
                    column_config={
                        "hero": "Hero",
                        "Pick_Count": "Matches Played",
                        "Win Rate %": st.column_config.ProgressColumn("Win Rate", format="%.1f%%", min_value=0, max_value=100)
                    },
                    hide_index=True
                )
                
                # Chart
                st.bar_chart(hero_stats.set_index('hero')['Win Rate %'])
