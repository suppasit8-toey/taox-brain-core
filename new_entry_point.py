# ==============================================================================
# SIDEBAR NAVIGATION & STATE
# ==============================================================================
init_session_state()

# ==============================================================================
with st.sidebar:
    st.title("TAOX BRAIN 🧠")
    
    # SYSTEM 1: VERSION SELECTOR
    selected_ver_name = "N/A" # Default safe value
    if db:
        versions = get_versions()
        version_opts = {v['name']: v['id'] for v in versions}
        
        if not versions:
            st.warning("No Patch Data Found.")
            if st.button("Initialize Season 1"):
                # Clean boot for first run
                clone_version(None, "Season 1 (Init)") 
                st.rerun()
        else:
            selected_ver_name = st.selectbox("Current Patch", list(version_opts.keys()))
            st.session_state['current_version_id'] = version_opts[selected_ver_name]
            st.caption(f"ID: {st.session_state['current_version_id']}")
    else:
        st.session_state['current_version_id'] = None

    st.markdown("---")
    
    # Ensure a default is selected
    selected_page = st.radio("Navigate", ["Hero Editor", "Synergy Builder", "Version Control"], index=0)

# ==============================================================================
# MAIN CONTENT ROUTER
# ==============================================================================

try:
    if selected_page == "Hero Editor":
        render_hero_editor_ui(selected_ver_name)
        
    elif selected_page == "Synergy Builder":
        st.header("Synergy Builder (Coming Soon)")
        st.info("Logic for Synergy Builder will be implemented here.")
        
    elif selected_page == "Version Control":
        st.header("Version Control")
        # Re-implementing the basic version creation UI
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Create New Patch")
            with st.form("new_patch_main"):
                new_v_name = st.text_input("New Version Name", "S1 2025 - Patch X")
                
                # Fetch opts again or assume context
                # To be safe, we rely on sidebar fetch if possible, but localized here is safer
                clone_opts = ["Empty"]
                # We can't access 'version_opts' from sidebar scope easily unless it's session state?
                # Actually it IS in local scope if this is one script. Yes.
                if 'version_opts' in locals():
                    clone_opts += list(version_opts.keys())
                
                clone_source = st.selectbox("Clone Data From", clone_opts)
                
                if st.form_submit_button("Create Version"):
                    if clone_source == "Empty":
                        if db:
                            db.collection('versions').add({
                                "name": new_v_name,
                                "created_at": datetime.now(),
                                "is_active": True
                            })
                            st.success(f"Created empty version: {new_v_name}")
                            time.sleep(1)
                            st.rerun()
                    else:
                        if db and 'version_opts' in locals():
                            src_id = version_opts.get(clone_source)
                            if src_id:
                                with st.spinner("Cloning Meta Data..."):
                                    clone_version(src_id, new_v_name)
                                st.success(f"Successfully cloned {clone_source} to {new_v_name}")
                                time.sleep(1)
                                st.rerun()

    else:
        st.error(f"Page '{selected_page}' not found!")

except Exception as e:
    st.error(f"💥 An error occurred: {e}")
    st.exception(e) # Show full traceback
