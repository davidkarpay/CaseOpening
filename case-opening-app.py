import streamlit as st
import json
from datetime import datetime, date
from pathlib import Path
import uuid
from modules.pdf_generator import generate_case_pdf
from modules.pdf_form_filler import fill_official_form
from modules.database import CaseDatabase
from modules.forms import render_defendant_info, render_case_info, render_court_info
from modules.utils import format_phone, parse_date, sanitize_case_data, validate_required_fields
from modules.auth_ui import check_authentication, show_user_info

# Page config
st.set_page_config(
    page_title="Case Opening Sheet Manager",
    page_icon="⚖️",
    layout="wide"
)

# Check authentication first
if not check_authentication():
    st.stop()

# Initialize directories
Path("data").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)
Path("exports/pdfs").mkdir(exist_ok=True)

# Initialize database
db = CaseDatabase("data/cases.json")

# Initialize session state
if 'current_case' not in st.session_state:
    st.session_state.current_case = {}
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'selected_case_id' not in st.session_state:
    st.session_state.selected_case_id = None

def clear_form():
    """Clear the current form"""
    st.session_state.current_case = {}
    st.session_state.edit_mode = False
    st.session_state.selected_case_id = None

def save_case():
    """Save current case to database with security validation"""
    case_data = st.session_state.current_case.copy()
    
    # Validate required fields
    is_valid, missing_fields = validate_required_fields(case_data)
    if not is_valid:
        st.error(f"Missing required fields: {', '.join(missing_fields)}")
        return None
    
    # Sanitize all input data
    case_data = sanitize_case_data(case_data)
    
    # Add metadata
    if not st.session_state.edit_mode:
        case_data['id'] = str(uuid.uuid4())
        case_data['created_at'] = datetime.now().isoformat()
    case_data['updated_at'] = datetime.now().isoformat()
    
    # Save to database
    try:
        if st.session_state.edit_mode:
            success = db.update_case(st.session_state.selected_case_id, case_data)
        else:
            success = db.add_case(case_data)
        
        if success:
            st.success("Case saved successfully!")
            return case_data
        else:
            st.error("Failed to save case. Please try again.")
            return None
    except Exception as e:
        st.error(f"Error saving case: {str(e)}")
        return None

# Main UI
st.title("⚖️ Case Opening Sheet Manager")
st.markdown("Manage case opening sheets with PDF export and searchable database")

# Sidebar for case management
with st.sidebar:
    st.header("📁 Case Management")
    
    # Show user info and logout
    show_user_info()
    
    # Page navigation
    page = st.selectbox(
        "📄 Navigate",
        ["📝 Case Management", "⚙️ Settings"],
        key="page_selection"
    )
    
    # New case button (only show on Case Management page)
    if page == "📝 Case Management":
        if st.button("➕ New Case", use_container_width=True, type="primary"):
            clear_form()
            st.rerun()
    
    # Search functionality
    st.subheader("🔍 Search Cases")
    search_term = st.text_input("Search by name or case number")
    
    # List cases
    cases = db.search_cases(search_term) if search_term else db.get_all_cases()
    
    if cases:
        st.subheader(f"📋 Cases ({len(cases)})")
        for case in cases:
            defendant_name = f"{case.get('last_name', '')}, {case.get('first_name', '')}"
            case_number = case.get('case_number', 'No case #')
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(
                    f"{defendant_name}\n{case_number}",
                    key=f"case_{case['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_case = case.copy()
                    st.session_state.edit_mode = True
                    st.session_state.selected_case_id = case['id']
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{case['id']}"):
                    db.delete_case(case['id'])
                    if st.session_state.selected_case_id == case['id']:
                        clear_form()
                    st.rerun()

# Main content area based on selected page
if page == "📝 Case Management":
    if st.session_state.edit_mode:
        st.info(f"📝 Editing case: {st.session_state.current_case.get('case_number', 'New Case')}")

    # Navigation shortcuts at the top
    col1, col2, col3, col4 = st.columns(4)
    with col1:
    if st.button("👤 Defendant Info", use_container_width=True):
        st.session_state.scroll_to = "defendant"
with col2:
    if st.button("📋 Case Details", use_container_width=True):
        st.session_state.scroll_to = "case"
with col3:
    if st.button("🏛️ Court Info", use_container_width=True):
        st.session_state.scroll_to = "court"
with col4:
    if st.button("📄 Export/View", use_container_width=True):
        st.session_state.scroll_to = "export"

st.divider()

# All forms on one page
# Defendant Information Section
st.markdown('<div id="defendant"></div>', unsafe_allow_html=True)
render_defendant_info(st.session_state.current_case)

st.divider()

# Case Details Section
st.markdown('<div id="case"></div>', unsafe_allow_html=True)
render_case_info(st.session_state.current_case)

st.divider()

# Court Information Section
st.markdown('<div id="court"></div>', unsafe_allow_html=True)
render_court_info(st.session_state.current_case)

st.divider()

# Export/View Section
st.markdown('<div id="export"></div>', unsafe_allow_html=True)
st.header("📄 Export and View")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Actions")
    
    # Save button
    if st.button("💾 Save Case", use_container_width=True, type="primary"):
        saved_case = save_case()
        st.success(f"✅ Case saved: {saved_case.get('case_number', 'New Case')}")
    
    # PDF Export Options
    st.markdown("### 📄 PDF Export Options")
    
    # Option 1: Custom PDF Report
    if st.button("📄 Generate Custom PDF Report", use_container_width=True):
        if st.session_state.current_case:
            pdf_path = generate_case_pdf(st.session_state.current_case)
            
            # Offer download
            with open(pdf_path, 'rb') as f:
                st.download_button(
                    label="⬇️ Download Custom Report",
                    data=f,
                    file_name=Path(pdf_path).name,
                    mime="application/pdf",
                    key="download_custom"
                )
    
    # Option 2: Fill Official Form
    if st.button("📋 Fill Official Case Opening Form", use_container_width=True):
        if st.session_state.current_case:
            try:
                # Check if template exists
                template_path = "CASE OPENING SHEET.pdf"
                if not Path(template_path).exists():
                    st.error(f"Template file '{template_path}' not found. Please ensure it's in the root directory.")
                else:
                    pdf_path = fill_official_form(st.session_state.current_case, template_path)
                    
                    # Offer download
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Official Form",
                            data=f,
                            file_name=Path(pdf_path).name,
                            mime="application/pdf",
                            key="download_official"
                        )
            except Exception as e:
                st.error(f"Error filling form: {str(e)}")
    
    # Export all data
    if st.button("📊 Export All Cases (JSON)", use_container_width=True):
        all_cases = db.get_all_cases()
        json_data = json.dumps(all_cases, indent=2)
        
        st.download_button(
            label="⬇️ Download All Cases",
            data=json_data,
            file_name=f"cases_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

with col2:
    st.subheader("Current Case Data")
    if st.session_state.current_case:
        st.json(st.session_state.current_case)
    else:
        st.info("No case data to display. Fill out the form to see the data structure.")

# Settings page
if page == "⚙️ Settings":
    from modules.settings_page import show_settings_page
    show_settings_page()

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center'>
        <p>Case Opening Sheet Manager v1.0 | Built for Public Defenders</p>
    </div>
    """,
    unsafe_allow_html=True
)