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

    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
        animation: auraMove 8s infinite alternate;
        pointer-events: none;
    }

    @keyframes auraMove {
        from { transform: scale(1) translate(-10%, -10%); }
        to { transform: scale(1.2) translate(10%, 10%); }
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
    c1, c2, c3 = st.columns([1, 4, 1])
    with c2:
        if os.path.exists('logo.png'): st.image('logo.png', use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 10px rgba(0,0,0,0.3);'>WELCOME TO CATG QUIZ</h1>", unsafe_allow_html=True)
    if st.button("GET STARTED"): 
        st.session_state.page = 'mode_selection'
        st.rerun()

elif st.session_state.page == 'mode_selection':
    st.markdown("<h2 style='text-align: center; color: white;'>Choose Your Mode</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='text-align:center; font-size:60px;'>👤</div>", unsafe_allow_html=True)
        if st.button("SINGLE PLAYER"):
            st.session_state.game_mode = 'single'
            st.session_state.leaderboard = []
            st.session_state.page = 'register'; st.rerun()
    with col2:
        st.markdown("<div style='text-align:center; font-size:60px;'>👥</div>", unsafe_allow_html=True)
        if st.button("MULTIPLAYER"):
            st.session_state.game_mode = 'multi'
            st.session_state.leaderboard = []
            st.session_state.page = 'register'; st.rerun()
    with col3:
        st.markdown("<div style='text-align:center; font-size:60px;'>🏠</div>", unsafe_allow_html=True)
        if st.button("PLAY WITH FRIENDS"):
            st.session_state.game_mode = 'room'
            GLOBAL_LB.clear()
            st.session_state.page = 'room_setup'; st.rerun()

elif st.session_state.page == 'room_setup':
    st.markdown("<h2 style='text-align: center; color: white;'>Friend Room Setup</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["CREATE ROOM", "JOIN ROOM"])
    
    with tab1:
        r_code = st.text_input("Create Room Code", value=str(random.randint(1000, 9999)))
        st.code(r_code, language="text") # This makes it easy to copy
        r_slots = st.slider("Available Spaces", 2, 10, 4)
        r_time = st.select_slider("Pick Time Limit (Minutes)", options=[1, 2, 3, 5, 10])
        if st.button("OPEN ROOM"):
            st.session_state.room_code = r_code
            st.session_state.is_host = True
            st.session_state.time_limit = r_time * 60
            GLOBAL_ROOMS[r_code] = {'players': [], 'started': False, 'time': r_time*60, 'slots': r_slots}
            st.session_state.page = 'register'; st.rerun()
            
    with tab2:
        join_code = st.text_input("Enter Room Code")
        if st.button("JOIN"):
            if join_code in GLOBAL_ROOMS:
                room_data = GLOBAL_ROOMS[join_code]
                if len(room_data['players']) >= room_data['slots']:
                    st.error(f"⚠️ Room Full! (Max {room_data['slots']} players)")
                elif room_data['started']:
                    st.error("⚠️ Game already started!")
                else:
                    st.session_state.room_code = join_code
                    st.session_state.is_host = False
                    st.session_state.time_limit = room_data['time']
                    st.session_state.page = 'register'; st.rerun()
            else: 
                st.error("Room code not found! Check with the creator.")
                
    if st.button("BACK"): st.session_state.page = 'mode_selection'; st.rerun()

elif st.session_state.page == 'register':
    title = f"Room: {st.session_state.room_code}" if st.session_state.game_mode == 'room' else "Player Entry"
    st.markdown(f"<h2 style='text-align: center; color: white;'>{title}</h2>", unsafe_allow_html=True)
    player_names = []
    if st.session_state.game_mode in ['single', 'room']:
        name = st.text_input("Enter Your Name", key="reg_name")
        if name: player_names.append(name)
    else:
        num_players = st.number_input("Number of Players", 2, 50, 2)
        cols = st.columns(2)
        for i in range(num_players):
            with cols[i % 2]:
                n = st.text_input(f"Player {i+1}", key=f"p_{i}")
                if n: player_names.append(n)

    if st.session_state.game_mode != 'room':
        limit = st.selectbox("Time Limit (Seconds)", [30, 60, 120, 300], index=1)
        st.session_state.time_limit = limit

    if st.button("START"):
        if player_names:
            st.session_state.multi_players = player_names
            st.session_state.questions_data = json.load(open('questions.json')) if os.path.exists('questions.json') else []
            if st.session_state.game_mode == 'room':
                GLOBAL_ROOMS[st.session_state.room_code]['players'].append(player_names[0])
                st.session_state.page = 'lobby'
            else: st.session_state.page = 'quiz_init'
            st.rerun()

elif st.session_state.page == 'lobby':
    @st.fragment(run_every=1)
    def lobby_sync():
        room = GLOBAL_ROOMS.get(st.session_state.room_code)
        if not st.session_state.is_host and room['started']:
            st.session_state.page = 'quiz_init'; st.rerun()
        st.markdown("<div class='question-box'>", unsafe_allow_html=True)
        st.write(f"### Joined Players ({len(room['players'])}/{room['slots']}):")
        for p in room['players']: st.write(f"✅ **{p}**")
        st.markdown("</div>", unsafe_allow_html=True)
        if st.session_state.is_host and st.button("START GAME FOR EVERYONE"):
            room['started'] = True
            st.session_state.page = 'quiz_init'; st.rerun()
    lobby_sync()

elif st.session_state.page == 'quiz_init':
    indices = list(range(len(st.session_state.questions_data)))
    random.shuffle(indices)
    st.session_state.update({
        'p_name': st.session_state.multi_players[st.session_state.current_player_idx],
        'start_time': time.time(), 'score': 0, 'current_step': 0, 'page': 'quiz',
        'shuffled_indices': indices, 'wrong_answers': []
    })
    st.rerun()

elif st.session_state.page == 'quiz':
    play_audio("background_music.mp3")
    high_speed_timer()
    if st.session_state.current_step < len(st.session_state.shuffled_indices):
        q_idx = st.session_state.shuffled_indices[st.session_state.current_step]
        q = st.session_state.questions_data[q_idx]
        st.markdown(f"<div class='question-box'><p style='opacity:0.6;'>PLAYER: {st.session_state.p_name.upper()}</p><h2>{q['question']}</h2></div>", unsafe_allow_html=True)
        for i, opt in enumerate(q['options']):
            if st.button(opt, key=f"qbtn_{st.session_state.current_step}_{i}_{st.session_state.p_name}"):
                if opt == q['answer']: st.session_state.score += 1
                else: st.session_state.wrong_answers.append({'q': q['question'], 'correct': q['answer'], 'yours': opt})
                st.session_state.current_step += 1
                st.rerun()
    else:
        entry = (st.session_state.p_name, st.session_state.score)
        st.session_state.leaderboard.append(entry)
        GLOBAL_LB.append(entry)
        st.session_state.page = 'summary'; st.rerun()

elif st.session_state.page == 'summary':
    st.markdown(f"<h1 style='text-align: center; color: white;'>Done, {st.session_state.p_name}!</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-box' style='text-align:center;'><h2>Score: {st.session_state.score}</h2></div>", unsafe_allow_html=True)
    
    if st.session_state.wrong_answers:
        with st.expander("🔍 REVIEW WRONG ANSWERS"):
            for item in st.session_state.wrong_answers:
                st.markdown(f"**Q:** {item['q']}\n\n- ❌ Yours: {item['yours']}\n- ✅ Correct: {item['correct']}\n---")

    has_next = st.session_state.game_mode == 'multi' and (st.session_state.current_player_idx + 1 < len(st.session_state.multi_players))
    cA, cB, cC = st.columns(3)
    if has_next:
        if cA.button("NEXT PLAYER"): 
            st.session_state.current_player_idx += 1
            st.session_state.page = 'quiz_init'; st.rerun()
    else:
        if cA.button("NEW GAME"): st.session_state.page = 'mode_selection'; st.rerun()
    if cB.button("LEADERBOARD"): st.session_state.page = 'final'; st.rerun()
    if cC.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()

elif st.session_state.page == 'final':
    play_audio("winner_sound.mp3.mp3", loop=False)
    source_lb = GLOBAL_LB if st.session_state.game_mode == 'room' else st.session_state.leaderboard
    
    clean_lb = []
    seen = set()
    for name, score in source_lb:
        if (name, score) not in seen:
            clean_lb.append((name, score))
            seen.add((name, score))
    sorted_lb = sorted(clean_lb, key=lambda x: x[1], reverse=True)
    
    if sorted_lb:
        top_score = sorted_lb[0][1]
        winners = [n.upper() for n, s in sorted_lb if s == top_score]
        st.markdown("<div class='winner-box'><h1 style='color: #8B4513; margin:0;'>🎉 CATG QUIZ WINNER 🎉</h1>", unsafe_allow_html=True)
        if len(winners) > 1: st.markdown(f"<h2>DRAW!</h2><p>{', '.join(winners)}</p>", unsafe_allow_html=True)
        else: st.markdown(f"<h1 style='font-size: 50px;'>{winners[0]}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3>{top_score} PTS</h3></div>", unsafe_allow_html=True)

    current_rank, last_score = 0, -1
    for i, (name, score) in enumerate(sorted_lb):
        if score != last_score: current_rank = i + 1
        last_score = score
        style, rank_label = ("gold", "1st") if current_rank == 1 else (("silver", "2nd") if current_rank == 2 else (("bronze", "3rd") if current_rank == 3 else ("standard", f"{current_rank}th")))
        st.markdown(f"<div class='podium-card {style}'>{rank_label}: {name.upper()} — {score} PTS</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button("BACK TO START"): st.session_state.page = 'mode_selection'; st.rerun()
    if c2.button("RESET SCORES"): 
        if st.session_state.game_mode != 'room': st.session_state.leaderboard = []
        else: GLOBAL_LB.clear()
        st.rerun()
    if c3.button("QUIT"): st.session_state.clear(); st.session_state.page = 'welcome'; st.rerun()
