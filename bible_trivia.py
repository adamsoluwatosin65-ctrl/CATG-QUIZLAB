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
    .silver { background: linear-gradient(90deg, #C0C0C0, #F5F5F5); color: #4F4F4F; border: 3px solid #A9A9A9; }
    .bronze { background: linear-gradient(90deg, #CD7F32, #FAEBD7); color: #5D2906; border: 3px solid #8B4513; }
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
            entry = (st.session_state.p_name, st.session_state.score)
            if entry not in st.session_state.leaderboard:
                st.session_state.leaderboard.append(entry)
                GLOBAL_LB.append(entry)
            st.session_state.page = 'summary'
            st.rerun()
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px; text-shadow: 1px 1px 5px black;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

# --- APP PAGES ---
if st.session_state.page == 'welcome':
    st.markdown("<h1 style='text-align: center; color: white;'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    # CLEAN START FOR ALL MODES
    st.session_state.leaderboard = []
    st.session_state.multi_players = []
    st.session_state.current_player_idx = 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("SINGLE PLAYER"):
            st.session_state.game_mode = 'single'
            st.session_state.page = 'register'; st.rerun()
    with col2:
        if st.button("MULTIPLAYER"):
            st.session_state.game_mode = 'multi'
            st.session_state.page = 'register'; st.rerun()
    with col3:
        if st.button("FRIEND ROOM"):
            st.session_state.game_mode = 'room'
            GLOBAL_LB.clear() 
            st.session_state.page = 'room_setup'; st.rerun()

elif st.session_state.page == 'room_setup':
    tab1, tab2 = st.tabs(["CREATE ROOM", "JOIN ROOM"])
    with tab1:
        r_code = st.text_input("Room Code", value=str(random.randint(1000, 9999)))
        if st.button("OPEN ROOM"):
            st.session_state.room_code = r_code
            st.session_state.is_host = True
            GLOBAL_ROOMS[r_code] = {'players': [], 'started': False, 'time': 60}
            st.session_state.page = 'register'; st.rerun()
    with tab2:
        join_code = st.text_input("Enter Room Code")
        if st.button("JOIN"):
            if join_code in GLOBAL_ROOMS:
                st.session_state.room_code = join_code
                st.session_state.is_host = False
                st.session_state.page = 'register'; st.rerun()

elif st.session_state.page == 'register':
    if st.session_state.game_mode in ['single', 'room']:
        name = st.text_input("Enter Your Name", key="reg_name")
        if st.button("START"):
            if name:
                st.session_state.multi_players = [name]
                all_qs = json.load(open('questions.json')) if os.path.exists('questions.json') else []
                st.session_state.questions_data = all_qs
                if st.session_state.game_mode == 'room':
                    GLOBAL_ROOMS[st.session_state.room_code]['players'].append(name)
                    st.session_state.page = 'lobby'
                else: st.session_state.page = 'quiz_init'
                st.rerun()
    else:
        num = st.number_input("Players", 2, 10, 2)
        p_names = []
        for i in range(num):
            n = st.text_input(f"Player {i+1}", key=f"p_{i}")
            if n: p_names.append(n)
        if st.button("START MULTIPLAYER"):
            if len(p_names) == num:
                st.session_state.multi_players = p_names
                st.session_state.questions_data = json.load(open('questions.json'))
                st.session_state.page = 'quiz_init'; st.rerun()

elif st.session_state.page == 'lobby':
    room = GLOBAL_ROOMS.get(st.session_state.room_code)
    st.write(f"Players Joined: {room['players']}")
    if not st.session_state.is_host and room.get('started'):
        st.session_state.page = 'quiz_init'; st.rerun()
    if st.session_state.is_host and st.button("START GAME FOR EVERYONE"):
        room['started'] = True
        st.session_state.page = 'quiz_init'; st.rerun()

elif st.session_state.page == 'quiz_init':
    indices = list(range(len(st.session_state.questions_data)))
    random.shuffle(indices)
    st.session_state.update({
        'p_name': st.session_state.multi_players[st.session_state.current_player_idx],
        'start_time': time.time(), 'score': 0, 'current_step': 0, 'time_limit': 60,
        'shuffled_indices': indices, 'page': 'quiz'
    })
    st.rerun()

elif st.session_state.page == 'quiz':
    high_speed_timer()
    if st.session_state.current_step < len(st.session_state.shuffled_indices):
        q_idx = st.session_state.shuffled_indices[st.session_state.current_step]
        q = st.session_state.questions_data[q_idx]
        
        st.markdown(f"<div class='question-box'><h3>{st.session_state.p_name}</h3><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
        
        # KEY STABILITY: Using step, index, and player name to prevent disappearances
        for i, opt in enumerate(q['options']):
            if st.button(opt, key=f"btn_{st.session_state.current_step}_{i}_{st.session_state.p_name}"):
                if opt == q['answer']: st.session_state.score += 1
                st.session_state.current_step += 1
                st.rerun()
    else:
        entry = (st.session_state.p_name, st.session_state.score)
        st.session_state.leaderboard.append(entry)
        GLOBAL_LB.append(entry)
        st.session_state.page = 'summary'; st.rerun()

elif st.session_state.page == 'summary':
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>{st.session_state.p_name}, you scored: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    if st.session_state.game_mode == 'multi' and (st.session_state.current_player_idx + 1 < len(st.session_state.multi_players)):
        if st.button("NEXT PLAYER"):
            st.session_state.current_player_idx += 1
            st.session_state.page = 'quiz_init'; st.rerun()
    else:
        if st.button("SEE WINNER"): st.session_state.page = 'final'; st.rerun()

elif st.session_state.page == 'final':
    # PLAY WINNER SONG
    play_audio("winner_sound.mp3.mp3", loop=False)
    
    source_lb = GLOBAL_LB if st.session_state.game_mode == 'room' else st.session_state.leaderboard
    # Clean duplicates
    clean_lb = []
    seen = set()
    for name, score in source_lb:
        if (name, score) not in seen:
            clean_lb.append((name, score))
            seen.add((name, score))
    
    sorted_lb = sorted(clean_lb, key=lambda x: x[1], reverse=True)
    
    # --- CATG WINNER ANNOUNCEMENT ---
    if sorted_lb:
        top_score = sorted_lb[0][1]
        winners = [n.upper() for n, s in sorted_lb if s == top_score]
        
        st.markdown("<div class='winner-box'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #8B4513; margin:0;'>🎉 CATG QUIZ WINNER 🎉</h1>", unsafe_allow_html=True)
        if len(winners) > 1:
            st.markdown(f"<h2 style='color: #5D2906;'>ITS A DRAW!</h2><p style='font-size:24px;'>{', '.join(winners)}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='color: #5D2906; font-size: 50px;'>{winners[0]}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #8B4513;'>SCORE: {top_score} PTS</h3>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- FULL LEADERBOARD ---
    st.markdown("<h2 style='text-align: center; color: white;'>Final Standings</h2>", unsafe_allow_html=True)
    current_rank = 0
    last_score = -1
    for i, (name, score) in enumerate(sorted_lb):
        if score != last_score:
            current_rank = i + 1
        last_score = score
        
        if current_rank == 1: style, rank_label = "gold", "🥇 1st"
        elif current_rank == 2: style, rank_label = "silver", "🥈 2nd"
        elif current_rank == 3: style, rank_label = "bronze", "🥉 3rd"
        else: style, rank_label = "standard", f"{current_rank}th"
        
        st.markdown(f"<div class='podium-card {style}'>{rank_label}: {name.upper()} — {score} PTS</div>", unsafe_allow_html=True)

    if st.button("PLAY AGAIN"):
        st.session_state.clear()
        st.rerun()
