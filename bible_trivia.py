# --- LOBBY PAGE WITH AUTO-UPDATE ---
if st.session_state.page == 'lobby':
    st.markdown(f"<h2 style='text-align: center; color: white;'>Lobby: {st.session_state.room_code}</h2>", unsafe_allow_html=True)
    
    # We put the player list and start logic inside a fragment that runs every 1 second
    @st.fragment(run_every=1)
    def lobby_sync():
        room = GLOBAL_ROOMS.get(st.session_state.room_code)
        
        if not room:
            st.error("Room connection lost.")
            return

        # Check if host started the game (for joined players)
        if room['started'] and not st.session_state.is_host:
            st.session_state.page = 'quiz_init'
            st.rerun()

        st.markdown("<div class='question-box'>", unsafe_allow_html=True)
        st.write(f"### Joined Players ({len(room['players'])}/{room['slots']}):")
        
        # Display the current player list from global storage
        for p in room['players']:
            st.write(f"✅ {p}")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.is_host:
            if st.button("START GAME FOR EVERYONE"):
                room['started'] = True
                st.session_state.page = 'quiz_init'
                st.rerun()
        else:
            st.info("⌛ Waiting for host to start... the screen will transition automatically.")

    # Execute the fragment
    lobby_sync()


