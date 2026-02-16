import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- GLOBAL SERVER STORAGE ---
@st.cache_resource
def get_global_rooms():
    return {}

@st.cache_resource
def get_global_leaderboard():
    return []

GLOBAL_ROOMS = get_global_rooms()
GLOBAL_LB = get_global_leaderboard()

# --- HIGH-END ANIMATED DESIGN (Original) ---
st.markdown("""
    <style>
    audio { display: none; }
    .stApp {
        background: linear-gradient(-45deg, #1e5631, #2a7a45, #a8e063, #f0f4f1);
        background-size: 400% 400%;
        animation: activeGradient 12s ease infinite;
        background-attachment: fixed;
    }
    @keyframes activeGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .question-box {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-left: 12px solid #1e5631;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        margin-bottom: 30px;
        color: #1e5631;
    }
    .winner-box {
        background: linear-gradient(135deg, #FFD700, #FFFACD);
        padding: 30px;
        border-radius: 20px;
        border: 5px solid #DAA520;
        text-align: center;
        margin-bottom: 30px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .podium-card {
        padding: 20px; border-radius: 15px; margin: 10px 0;
        text-align: center; font-weight: 900; font-size: 22px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; font-size: 18px; font-weight: bold; }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 4.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: 2px solid #1e5631; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False
if 'game_mode' not in st.session_state: st.session_state.game_mode = 'single'
if 'multi_players' not in st.session_state: st.session_state.multi_players = []
if 'current_player_idx' not in st.session_state: st.session_state.current_player_idx = 0
if 'room_code' not in st.session_state: st.session_state.room_code = ""
if 'is_host' not in st.session_state: st.session_state.is_host = False
if 'confirm_quit' not in st.session_state: st.session_state.confirm_quit = False

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

# --- FIXED NAVIGATION FOOTER ---
def nav_footer(back_to=None):
    st.write("---")
    c1, c2 = st.columns(2)
    
    if back_to:
        if c1.button("⬅️ BACK", key=f"back_btn_{st.session_state.page}"):
            st.session_state.confirm_quit = False
            st.session_state.page = back_to
            st.rerun()
            
    if not st.session_state.confirm_quit:
        if c2.button("🚪 QUIT GAME", key=f"quit_btn_{st.session_state.page}"):
            st.session_state.confirm_quit = True
            st.rerun()
    else:
        with st.container():
            st.warning("Are you sure you want to quit?")
            k1, k2 = st.columns(2)
            if k1.button("✅ YES", key=f"yes_{st.session_state.page}"):
                st.session_state.clear()
                st.rerun()
            if k2.button("❌ NO", key=f"no_{st.session_state.page}"):
                st.session_state.confirm_quit = False
                st.rerun()

@st.fragment(run_every=1)
def high_speed_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            entry = (st.session_state.p_name, st.session_state.score)
            if entry not in st.session_state.leaderboard:
                st.session_state.leaderboard.append(entry)
                GLOBAL_LB.append(entry)
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- APP PAGES ---
if st.session_state.page == 'welcome':
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    st.markdown("<h2 style='text-align: center; color: white;'>Choose Your Mode</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("SINGLE"): st.session_state.game_mode = 'single'; st.session_state.page = 'register'; st.rerun()
    if c2.button("MULTI"): st.session_state.game_mode = 'multi'; st.session_state.page = 'register'; st.rerun()
    if c3.button("FRIENDS"): st.session_state.game_mode = 'room'; st.session_state.page = 'room_setup'; st.rerun()
    nav_footer(back_to='welcome')

elif st.session_state.page == 'room_setup':
    t1, t2 = st.tabs(["CREATE", "JOIN"])
    with t1:
        r_code = st.text_input("Room Code", value=str(random.randint(1000, 9999)))
        r_slots = st.slider("Max Players", 2, 30, 10)
        if st.button("OPEN ROOM"):
            st.session_state.update({'room_code':r_code, 'is_host':True, 'time_limit':60})
            GLOBAL_ROOMS[r_code] = {'players': [], 'started': False, 'time': 60, 'slots': r_slots}
            st.session_state.page = 'register'; st.rerun()
    with t2:
        join_code = st.text_input("Enter Room Code")
        if st.button("JOIN ROOM"):
            if join_code in GLOBAL_ROOMS:
                st.session_state.update({'room_code':join_code, 'is_host':False, 'page':'register'})
                st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'register':
    name = st.text_input("Your Name")
    if st.button("GO"):
        if name:
            st.session_state.multi_players = [name]
            st.session_state.questions_data = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            if st.session_state.game_mode == 'room':
                GLOBAL_ROOMS[st.session_state.room_code]['players'].append(name)
                st.session_state.page = 'lobby'
            else: st.session_state.page = 'quiz_init'
            st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'lobby':
    @st.fragment(run_every=1)
    def lobby_sync():
        room = GLOBAL_ROOMS.get(st.session_state.room_code)
        st.write(f"Players: {room['players']}")
        if st.session_state.is_host and st.button("START"):
            room['started'] = True; st.session_state.page = 'quiz_init'; st.rerun()
        if not st.session_state.is_host and room['started']:
            st.session_state.page = 'quiz_init'; st.rerun()
    lobby_sync()
    nav_footer(back_to='room_setup')

elif st.session_state.page == 'quiz_init':
    st.session_state.update({'p_name': st.session_state.multi_players[0], 'start_time': time.time(), 'score': 0, 'current_step': 0, 'page': 'quiz', 'shuffled_indices': list(range(len(st.session_state.questions_data))), 'wrong_answers': []})
    st.rerun()

elif st.session_state.page == 'quiz':
    high_speed_timer()
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    for i, opt in enumerate(q['options']):
        if st.button(opt, key=f"ans_{st.session_state.current_step}_{i}"):
            if opt == q['answer']: st.session_state.score += 1
            else: st.session_state.wrong_answers.append({'q': q['question'], 'correct': q['answer'], 'yours': opt})
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.questions_data):
                st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
                st.session_state.page = 'summary'
            st.rerun()
    nav_footer(back_to='register')

elif st.session_state.page == 'summary':
    st.write(f"# {st.session_state.p_name}: {st.session_state.score}")
    if st.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    for i, (n, s) in enumerate(st.session_state.leaderboard):
        st.write(f"{i+1}. {n} - {s}")
    nav_footer(back_to='mode_selection')
