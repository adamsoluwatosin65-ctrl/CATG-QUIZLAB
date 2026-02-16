import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- SHARED ROOM DATABASE (Simulated Persistence) ---
ROOMS_FILE = "quiz_rooms.json"

def load_rooms():
    if os.path.exists(ROOMS_FILE):
        with open(ROOMS_FILE, "r") as f: return json.load(f)
    return {}

def save_rooms(data):
    with open(ROOMS_FILE, "w") as f: json.dump(data, f)

# --- HIGH-END ANIMATED DESIGN ---
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
    .podium-card {
        padding: 20px; border-radius: 15px; margin: 10px 0;
        text-align: center; font-weight: 900; font-size: 22px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; }
    .silver { background: linear-gradient(90deg, #C0C0C0, #F5F5F5); color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: linear-gradient(90deg, #CD7F32, #FAEBD7); color: #5D2906; border: 3px solid #8B4513; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; font-size: 18px; font-weight: bold; }
    .stButton>button { 
        width: 100%; border-radius: 20px; height: 4.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: 2px solid #1e5631; 
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #1e5631 !important; color: white !important; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False
if 'game_mode' not in st.session_state: st.session_state.game_mode = 'single'
if 'room_code' not in st.session_state: st.session_state.room_code = None

def play_audio(file_path, loop=True):
    if not st.session_state.muted and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

@st.fragment(run_every=1)
def high_speed_timer():
    if st.session_state.page == 'quiz' and 'start_time' in st.session_state:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.time_limit - elapsed)
        if remaining <= 0:
            submit_score()
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

def submit_score():
    # Local leaderboard
    if (st.session_state.p_name, st.session_state.score) not in st.session_state.leaderboard:
        st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
    
    # Room leaderboard (Friends mode)
    if st.session_state.game_mode == 'friends' and st.session_state.room_code:
        rooms = load_rooms()
        code = st.session_state.room_code
        if code in rooms:
            rooms[code]['scores'][st.session_state.p_name] = st.session_state.score
            save_rooms(rooms)

# --- APP PAGES ---

if st.session_state.page == 'welcome':
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    st.markdown("<h2 style='text-align: center; color: white;'>Choose Your Mode</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div style='text-align:center; font-size:60px;'>👤</div>", unsafe_allow_html=True)
        if st.button("SINGLE"):
            st.session_state.game_mode = 'single'
            st.session_state.page = 'register'
            st.rerun()
    with c2:
        st.markdown("<div style='text-align:center; font-size:60px;'>👥</div>", unsafe_allow_html=True)
        if st.button("MULTIPLAYER"):
            st.session_state.game_mode = 'multi'
            st.session_state.page = 'register'
            st.rerun()
    with c3:
        st.markdown("<div style='text-align:center; font-size:60px;'>🌐</div>", unsafe_allow_html=True)
        if st.button("WITH FRIENDS"):
            st.session_state.game_mode = 'friends'
            st.session_state.page = 'friends_lobby'
            st.rerun()

elif st.session_state.page == 'friends_lobby':
    st.markdown("<h2 style='text-align: center; color: white;'>Play With Friends</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Create Room", "Join Room"])
    
    with tab1:
        r_name = st.text_input("Your Name", key="f_host_name")
        r_limit = st.slider("Time Limit (Sec)", 30, 600, 60)
        r_cap = st.number_input("Max Players", 2, 20, 5)
        if st.button("CREATE ROOM"):
            code = str(random.randint(1000, 9999))
            rooms = load_rooms()
            rooms[code] = {"limit": r_limit, "cap": r_cap, "scores": {}, "created_at": time.time()}
            save_rooms(rooms)
            st.session_state.room_code = code
            st.session_state.p_name = r_name
            st.session_state.time_limit = r_limit
            st.success(f"Room Created! Code: {code}")
            if st.button("START AS HOST"):
                all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
                st.session_state.questions_data = all_qs
                st.session_state.page = 'quiz_init'
                st.rerun()

    with tab2:
        j_name = st.text_input("Your Name", key="f_join_name")
        j_code = st.text_input("Enter 4-Digit Code")
        if st.button("JOIN"):
            rooms = load_rooms()
            if j_code in rooms:
                if len(rooms[j_code]['scores']) < rooms[j_code]['cap']:
                    st.session_state.room_code = j_code
                    st.session_state.p_name = j_name
                    st.session_state.time_limit = rooms[j_code]['limit']
                    all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
                    st.session_state.questions_data = all_qs
                    st.session_state.page = 'quiz_init'
                    st.rerun()
                else: st.error("Room is full!")
            else: st.error("Room not found!")

elif st.session_state.page == 'register':
    # [YOUR ORIGINAL REGISTER LOGIC REMAINS HERE UNTOUCHED]
    st.markdown("<h2 style='text-align: center; color: white;'>Entry</h2>", unsafe_allow_html=True)
    player_names = []
    if st.session_state.game_mode == 'single':
        name = st.text_input("Player Name")
        if name: player_names.append(name)
    else:
        num_players = st.number_input("Number of Players", 2, 50, 2)
        cols = st.columns(2)
        for i in range(num_players):
            with cols[i%2]:
                n = st.text_input(f"P{i+1}", key=f"pname_{i}")
                if n: player_names.append(n)
    
    limit = st.selectbox("Limit", [30, 60, 120], index=1)
    if st.button("START"):
        all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
        st.session_state.update({'multi_players': player_names, 'current_player_idx': 0, 'time_limit': limit, 'questions_data': all_qs, 'page': 'quiz_init'})
        st.rerun()

elif st.session_state.page == 'quiz_init':
    # Setup for the individual player
    if st.session_state.game_mode != 'friends':
        st.session_state.p_name = st.session_state.multi_players[st.session_state.current_player_idx]
    
    indices = list(range(len(st.session_state.questions_data)))
    random.shuffle(indices)
    st.session_state.update({'start_time': time.time(), 'score': 0, 'shuffled_indices': indices, 'current_step': 0, 'wrong_answers': [], 'page': 'quiz'})
    st.rerun()

elif st.session_state.page == 'quiz':
    high_speed_timer()
    step = st.session_state.current_step
    if step < len(st.session_state.shuffled_indices):
        q = st.session_state.questions_data[st.session_state.shuffled_indices[step]]
        st.markdown(f'<div class="question-box"><h2>{q["question"]}</h2></div>', unsafe_allow_html=True)
        for opt in q['options']:
            if st.button(opt, key=f"q{step}_{opt}"):
                if opt == q['answer']: st.session_state.score += 1
                else: st.session_state.wrong_answers.append({'question': q['question'], 'correct': q['answer'], 'yours': opt})
                st.session_state.current_step += 1
                st.rerun()
    else:
        submit_score()
        st.session_state.page = 'summary'
        st.rerun()

elif st.session_state.page == 'summary':
    st.markdown(f"<h1 style='text-align: center; color: white;'>Done, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    
    if st.button("LEADERBOARD"): 
        st.session_state.page = 'final'
        st.rerun()

elif st.session_state.page == 'final':
    st.markdown("<h1 style='text-align: center; color: white;'>🏆 ROOM RANKINGS 🏆</h1>", unsafe_allow_html=True)
    
    if st.session_state.game_mode == 'friends' and st.session_state.room_code:
        rooms = load_rooms()
        room_scores = rooms.get(st.session_state.room_code, {}).get('scores', {})
        display_list = sorted(room_scores.items(), key=lambda x: x[1], reverse=True)
    else:
        display_list = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)

    for i, (n, s) in enumerate(display_list):
        style = "gold" if i == 0 else "silver" if i == 1 else "bronze" if i == 2 else "standard"
        st.markdown(f"<div class='podium-card {style}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
    
    if st.button("EXIT TO MAIN MENU"):
        st.session_state.clear()
        st.rerun()
