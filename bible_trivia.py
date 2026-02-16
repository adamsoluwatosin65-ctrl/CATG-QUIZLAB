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

# --- ULTRA-FINE UI & ANIMATIONS ---
st.markdown("""
    <style>
    audio { display: none; }
    
    /* Dynamic Animated Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, #0a2e1a, #1e5631, #2a7a45, #143d21);
        background-size: 400% 400%;
        animation: activeGradient 15s ease infinite;
        background-attachment: fixed;
    }
    @keyframes activeGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Floating Aura Effect */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 50% 50%, rgba(168, 224, 99, 0.15) 0%, transparent 70%);
        animation: auraMove 10s infinite alternate;
        pointer-events: none;
    }
    @keyframes auraMove {
        from { transform: scale(1) translate(-5%, -5%); }
        to { transform: scale(1.3) translate(5%, 5%); }
    }

    /* Glassmorphism Home Card */
    .home-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 40px;
        padding: 50px 20px;
        text-align: center;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        margin-top: 20px;
        animation: slideUp 1.2s ease-out;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Elegant Typography */
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 3.5rem !important;
        color: white;
        text-shadow: 0 10px 20px rgba(0,0,0,0.2);
        letter-spacing: -2px;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        color: #a8e063;
        font-size: 1.2rem;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 30px;
    }

    /* Question & Box Styling */
    .question-box {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        padding: 40px;
        border-radius: 30px;
        border-left: 12px solid #1e5631;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        margin-bottom: 30px;
        color: #1e5631;
    }

    /* Custom Button Animation */
    .stButton>button { 
        width: 100%; border-radius: 25px; height: 4.5em; 
        font-size: 18px; font-weight: 800; 
        background: white; color: #1e5631; border: none; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { 
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 30px rgba(0,0,0,0.2);
        background-color: #a8e063 !important;
        color: #1e5631 !important;
    }

    /* Glowing Start Button specific to Home */
    .start-btn button {
        background: linear-gradient(90deg, #ffffff, #f0f4f1) !important;
        border: 2px solid #a8e063 !important;
        animation: pulseGlow 2s infinite;
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(168, 224, 99, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(168, 224, 99, 0); }
        100% { box-shadow: 0 0 0 0 rgba(168, 224, 99, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'welcome'
if 'leaderboard' not in st.session_state: st.session_state.leaderboard = []
if 'muted' not in st.session_state: st.session_state.muted = False
if 'game_mode' not in st.session_state: st.session_state.game_mode = 'single'
if 'multi_players' not in st.session_state: st.session_state.multi_players = []
if 'room_code' not in st.session_state: st.session_state.room_code = ""
if 'is_host' not in st.session_state: st.session_state.is_host = False
if 'confirm_quit' not in st.session_state: st.session_state.confirm_quit = False

def play_audio(file_path, loop=True):
    if not st.session_state.get('muted', False) and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            st.audio(f.read(), format="audio/mp3", loop=loop, autoplay=True)

def nav_footer(back_to=None):
    st.write("---")
    c1, c2, c3 = st.columns(3)
    m_label = "🔊 UNMUTE" if st.session_state.muted else "🔇 MUTE"
    if c1.button(m_label, key=f"nav_m_{st.session_state.page}"):
        st.session_state.muted = not st.session_state.muted
        st.rerun()
    if back_to:
        if c2.button("⬅️ BACK", key=f"nav_b_{st.session_state.page}"):
            st.session_state.confirm_quit = False
            st.session_state.page = back_to
            st.rerun()
    if not st.session_state.confirm_quit:
        if c3.button("🚪 QUIT", key=f"nav_q_{st.session_state.page}"):
            st.session_state.confirm_quit = True
            st.rerun()
    else:
        st.warning("Quit game?")
        k1, k2 = st.columns(2)
        if k1.button("✅ YES", key=f"q_y_{st.session_state.page}"):
            st.session_state.clear()
            st.rerun()
        if k2.button("❌ NO", key=f"q_n_{st.session_state.page}"):
            st.session_state.confirm_quit = False
            st.rerun()

# --- PAGES ---
if st.session_state.page == 'welcome':
    st.markdown('<div class="home-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if os.path.exists('logo.png'): 
            st.image('logo.png', use_container_width=True)
    st.markdown('<h1 class="hero-title">CATG QUIZ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">The Ultimate Pro Challenge</p>', unsafe_allow_html=True)
    
    # Glowing Button Wrapper
    st.markdown('<div class="start-btn">', unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.page == 'mode_selection':
    st.markdown("<h2 style='text-align: center; color: white;'>Choose Your Mode</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='text-align:center; font-size:60px;'>👤</div>", unsafe_allow_html=True)
        if st.button("SINGLE PLAYER"):
            st.session_state.game_mode = 'single'; st.session_state.page = 'register'; st.rerun()
    with col2:
        st.markdown("<div style='text-align:center; font-size:60px;'>👥</div>", unsafe_allow_html=True)
        if st.button("MULTIPLAYER"):
            st.session_state.game_mode = 'multi'; st.session_state.page = 'register'; st.rerun()
    with col3:
        st.markdown("<div style='text-align:center; font-size:60px;'>🏠</div>", unsafe_allow_html=True)
        if st.button("FRIENDS ROOM"):
            st.session_state.game_mode = 'room'; st.session_state.page = 'room_setup'; st.rerun()
    nav_footer(back_to='welcome')

elif st.session_state.page == 'room_setup':
    st.markdown("<h2 style='text-align: center; color: white;'>Friend Room Setup</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["CREATE ROOM", "JOIN ROOM"])
    with tab1:
        r_code = st.text_input("Room Code", value=str(random.randint(1000, 9999)))
        st.code(r_code)
        r_slots = st.slider("Max Players", 2, 30, 4)
        r_time = st.select_slider("Time Limit (Mins)", options=[1, 2, 3, 5, 10])
        if st.button("OPEN ROOM"):
            st.session_state.update({'room_code': r_code, 'is_host': True, 'time_limit': r_time * 60})
            GLOBAL_ROOMS[r_code] = {'players': [], 'started': False, 'time': r_time*60, 'slots': r_slots}
            st.session_state.page = 'register'; st.rerun()
    with tab2:
        join_code = st.text_input("Enter Code")
        if st.button("JOIN"):
            if join_code in GLOBAL_ROOMS:
                room = GLOBAL_ROOMS[join_code]
                if len(room['players']) < room['slots'] and not room['started']:
                    st.session_state.update({'room_code': join_code, 'is_host': False, 'time_limit': room['time'], 'page': 'register'})
                    st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'register':
    name = st.text_input("Enter Name")
    if st.button("START"):
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
        st.markdown(f"<h2 style='text-align: center; color: white;'>ROOM CODE: {st.session_state.room_code}</h2>", unsafe_allow_html=True)
        if not st.session_state.is_host and room['started']: st.session_state.page = 'quiz_init'; st.rerun()
        st.markdown("<div class='question-box'>", unsafe_allow_html=True)
        st.write(f"### Players ({len(room['players'])}/{room['slots']}):")
        for p in room['players']: st.write(f"✅ {p}")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.session_state.is_host and st.button("GO!"):
            room['started'] = True; st.session_state.page = 'quiz_init'; st.rerun()
    lobby_sync()
    nav_footer(back_to='room_setup')

elif st.session_state.page == 'quiz_init':
    st.session_state.update({'p_name': st.session_state.multi_players[0], 'start_time': time.time(), 'score': 0, 'current_step': 0, 'page': 'quiz', 'shuffled_indices': list(range(len(st.session_state.questions_data))), 'wrong_answers': []})
    random.shuffle(st.session_state.shuffled_indices)
    st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    for i, opt in enumerate(q['options']):
        if st.button(opt, key=f"q_{st.session_state.current_step}_{i}"):
            if opt == q['answer']: st.session_state.score += 1
            else: st.session_state.wrong_answers.append({'q': q['question'], 'correct': q['answer'], 'yours': opt})
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.questions_data):
                st.session_state.leaderboard.append((st.session_state.p_name, st.session_state.score))
                st.session_state.page = 'summary'
            st.rerun()
    nav_footer(back_to='register')

elif st.session_state.page == 'summary':
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    if st.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    sorted_lb = sorted(st.session_state.leaderboard, key=lambda x: x[1], reverse=True)
    if sorted_lb:
        st.markdown(f"<div class='winner-box'><h1>🏆 {sorted_lb[0][0].upper()} 🏆</h1></div>", unsafe_allow_html=True)
        for i, (n, s) in enumerate(sorted_lb):
            st.markdown(f"<div class='podium-card standard'>{i+1}. {n.upper()} - {s} PTS</div>", unsafe_allow_html=True)
    nav_footer(back_to='mode_selection')
