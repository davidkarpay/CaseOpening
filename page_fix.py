# Quick fix for the page structure
# Add this after the sidebar and before the footer

# Main content area based on selected page
if page == "📝 Case Management":
    # Case management content goes here
    if st.session_state.edit_mode:
        st.info(f"📝 Editing case: {st.session_state.current_case.get('case_number', 'New Case')}")
    
    # ... all the case management content should be indented here
    
elif page == "⚙️ Settings":
    from modules.settings_page import show_settings_page
    show_settings_page()