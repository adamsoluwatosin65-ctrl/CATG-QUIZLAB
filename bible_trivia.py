import streamlit as st
import json, time, os, random

# --- PAGE CONFIG ---
st.set_page_config(page_title="CATG Quiz Pro", layout="centered")

# --- GLOBAL SERVER STORAGE ---
@st.cache_resource
def get_global_rooms(): return {}
@st.cache_resource
def get_global_leaderboard(): return []

GLOBAL_ROOMS = get_global_rooms()
GLOBAL_LB = get_global_leaderboard()

# --- ULTRA-FINE UI & ANIMATIONS ---
st.markdown("""
    <style>
    audio { display: none; }
    
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

    /* Floating Balloons Animation */
    .balloon {
        position: fixed; bottom: -100px;
        width: 50px; height: 70px;
        background: rgba(168, 224, 99, 0.7);
        border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
        animation: floatUp 6s infinite ease-in;
        z-index: 0;
    }
    @keyframes floatUp {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-120vh) rotate(20deg); opacity: 0; }
    }

    .home-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 40px; padding: 50px 20px; text-align: center;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3); margin-top: 20px;
    }

    .hero-title { font-weight: 900; font-size: 2.2rem !important; color: white; text-shadow: 0 5px 15px rgba(0,0,0,0.3); }
    .hero-subtitle { color: #a8e063; font-size: 1.1rem; font-weight: 600; text-transform: uppercase; }

    .question-box {
        background: rgba(255, 255, 255, 0.9);
        padding: 40px; border-radius: 30px; border-left: 12px solid #1e5631;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2); color: #1e5631;
    }

    .winner-box {
        background: linear-gradient(135deg, #FFD700, #FFFACD);
        padding: 30px; border-radius: 20px; border: 5px solid #DAA520;
        text-align: center; margin-bottom: 30px; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

    .podium-card { padding: 20px; border-radius: 15px; margin: 10px 0; text-align: center; font-weight: 900; }
    .gold { background: linear-gradient(90deg, #FFD700, #FFFACD); color: #8B4513; border: 3px solid #DAA520; font-size: 24px; }
    .standard { background: white; color: #1e5631; border: 1px solid #ddd; font-size: 18px; }

    .stButton>button { 
        width: 100%; border-radius: 25px; height: 4.5em; 
        font-size: 18px; font-weight: 800; background: white; color: #1e5631; 
        border: 2px solid #1e5631; transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #a8e063 !important; transform: scale(1.02); }
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
if 'time_limit' not in st.session_state: st.session_state.time_limit = 60

def play_audio(file_path, loop=True):
    if not st.session_state.get('muted', False) and os.path.exists(file_path):
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
        st.markdown(f"<div style='text-align:right; font-weight:900; color:white; font-size:24px;'>⏱️ {remaining}s</div>", unsafe_allow_html=True)

def nav_footer(back_to=None):
    st.write("---")
    c1, c2, c3 = st.columns(3)
    m_label = "🔊 UNMUTE" if st.session_state.muted else "🔇 MUTE"
    if c1.button(m_label, key=f"nav_m_{st.session_state.page}"):
        st.session_state.muted = not st.session_state.muted
        st.rerun()
    if back_to:
        if c2.button("⬅️ BACK", key=f"nav_b_{st.session_state.page}"):
            st.session_state.confirm_quit = False; st.session_state.page = back_to; st.rerun()
    if not st.session_state.confirm_quit:
        if c3.button("🚪 QUIT", key=f"nav_q_{st.session_state.page}"):
            st.session_state.confirm_quit = True; st.rerun()
    else:
        st.warning("Quit & Reset All Data?")
        k1, k2 = st.columns(2)
        if k1.button("✅ YES", key=f"q_y_{st.session_state.page}"): 
            # RESET GLOBAL STORAGE
            GLOBAL_LB.clear()
            GLOBAL_ROOMS.clear()
            st.session_state.clear(); 
            st.rerun()
        if k2.button("❌ NO", key=f"q_n_{st.session_state.page}"): st.session_state.confirm_quit = False; st.rerun()

# --- PAGES ---
if st.session_state.page == 'welcome':
    st.markdown('<div class="home-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
    st.markdown('<h1 class="hero-title">WELCOME CHRISTIAN ALL ACROSS THE GLOBE QUIZ</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Win to get to leadership board</p>', unsafe_allow_html=True)
    if st.button("GET STARTED"): st.session_state.page = 'mode_selection'; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'mode_selection':
    st.markdown("<h2 style='text-align: center; color: white;'>Choose Your Mode</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    if col1.button("👤 SINGLE"): st.session_state.game_mode = 'single'; st.session_state.page = 'register'; st.rerun()
    if col2.button("👥 MULTI"): st.session_state.game_mode = 'multi'; st.session_state.page = 'register'; st.rerun()
    if col3.button("🏠 ROOM"): st.session_state.game_mode = 'room'; st.session_state.page = 'room_setup'; st.rerun()
    nav_footer(back_to='welcome')

elif st.session_state.page == 'room_setup':
    t1, t2 = st.tabs(["CREATE", "JOIN"])
    with t1:
        r_code = st.text_input("Room Code", value=str(random.randint(1000, 9999)))
        r_slots = st.slider("Max Players", 2, 30, 4)
        r_time = st.select_slider("Time (Mins)", options=[1, 2, 3, 5])
        if st.button("OPEN ROOM"):
            st.session_state.update({'room_code': r_code, 'is_host': True, 'time_limit': r_time * 60})
            GLOBAL_ROOMS[r_code] = {'players': [], 'started': False, 'time': r_time*60, 'slots': r_slots}
            st.session_state.page = 'register'; st.rerun()
    with t2:
        join_code = st.text_input("Enter Code")
        if st.button("JOIN"):
            if join_code in GLOBAL_ROOMS:
                room = GLOBAL_ROOMS[join_code]
                st.session_state.update({'room_code': join_code, 'is_host': False, 'time_limit': room['time'], 'page': 'register'})
                st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'register':
    name = st.text_input("Enter Name")
    if st.session_state.game_mode != 'room':
        st.session_state.time_limit = st.selectbox("Timer (Sec)", [30, 60, 120, 300], index=1)
    if st.button("PROCEED"):
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
        st.markdown(f"<h2 style='text-align: center; color: white;'>ROOM: {st.session_state.room_code}</h2>", unsafe_allow_html=True)
        if not st.session_state.is_host and room['started']: st.session_state.page = 'quiz_init'; st.rerun()
        st.markdown("<div class='question-box'>", unsafe_allow_html=True)
        st.write(f"### Players: {len(room['players'])}/{room['slots']}")
        for p in room['players']: st.write(f"✅ {p}")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.session_state.is_host and st.button("START"): room['started'] = True; st.session_state.page = 'quiz_init'; st.rerun()
    lobby_sync()
    nav_footer(back_to='room_setup')

elif st.session_state.page == 'quiz_init':
    st.session_state.update({'p_name': st.session_state.multi_players[0], 'start_time': time.time(), 'score': 0, 'current_step': 0, 'page': 'quiz', 'shuffled_indices': list(range(len(st.session_state.questions_data))), 'wrong_answers': []})
    random.shuffle(st.session_state.shuffled_indices)
    st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    high_speed_timer()
    q = st.session_state.questions_data[st.session_state.shuffled_indices[st.session_state.current_step]]
    st.markdown(f"<div class='question-box'><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
    for i, opt in enumerate(q['options']):
        if st.button(opt, key=f"q_{st.session_state.current_step}_{i}"):
            if opt == q['answer']: st.session_state.score += 1
            else: st.session_state.wrong_answers.append({'q': q['question'], 'correct': q['answer'], 'yours': opt})
            st.session_state.current_step += 1
            if st.session_state.current_step >= len(st.session_state.questions_data):
                entry = (st.session_state.p_name, st.session_state.score)
                if entry not in st.session_state.leaderboard: 
                    st.session_state.leaderboard.append(entry)
                    GLOBAL_LB.append(entry)
                st.session_state.page = 'summary'
            st.rerun()
    nav_footer(back_to='register')

elif st.session_state.page == 'summary':
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Your Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    
    if st.session_state.get('wrong_answers'):
        with st.expander("🔍 REVIEW FAILED ANSWERS", expanded=False):
            for item in st.session_state.wrong_answers:
                st.markdown(f"""
                **Question:** {item['q']}  
                * ❌ **Yours:** <span style="color:red;">{item['yours']}</span>  
                * ✅ **Correct:** <span style="color:green;">{item['correct']}</span>
                <hr style="margin:10px 0;">
                """, unsafe_allow_html=True)
    else:
        st.success("Perfect Score! You are a Bible Scholar! ✨")

    if st.button("GO TO LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    nav_footer(back_to='mode_selection')

elif st.session_state.page == 'final':
    for i in range(10): st.markdown(f'<div class="balloon" style="left:{random.randint(0,90)}%; animation-delay:{random.random()*5}s;"></div>', unsafe_allow_html=True)
    play_audio("winner_sound.mp3.mp3", loop=False)
    
    source_lb = GLOBAL_LB if st.session_state.game_mode == 'room' else st.session_state.leaderboard
    sorted_lb = sorted(source_lb, key=lambda x: x[1], reverse=True)
    
    if sorted_lb:
        st.markdown(f"<div class='winner-box'><h1>🏆 THE WINNER 🏆</h1><h2>{sorted_lb[0][0].upper()}</h2><h3>{sorted_lb[0][1]} POINTS</h3></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:white; text-align:center;'>Leadership Board</h2>", unsafe_allow_html=True)
        for i, (n, s) in enumerate(sorted_lb):
            style = "gold" if i == 0 else "standard"
            st.markdown(f"<div class='podium-card {style}'>{i+1}. {n.upper()} — {s} PTS</div>", unsafe_allow_html=True)
    nav_footer(back_to='mode_selection')
