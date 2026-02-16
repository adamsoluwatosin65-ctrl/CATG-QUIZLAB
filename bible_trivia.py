elif st.session_state.page == 'room_setup':
    # RESTORED: SLIDERS AND TAB LOGIC + FULL JOIN ROOM FUNCTIONALITY
    st.markdown("<h2 style='text-align: center; color: white;'>Friend Room Setup</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["CREATE ROOM", "JOIN ROOM"])
    
    with tab1:
        r_code = st.text_input("Create Room Code", value=str(random.randint(1000, 9999)))
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
                    st.session_state.page = 'register'
                    st.rerun()
            else: 
                st.error("Room code not found! Check with the creator.")
                
    if st.button("BACK"): 
        st.session_state.page = 'mode_selection'
        st.rerun()
