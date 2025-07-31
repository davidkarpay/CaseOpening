"""
Forms module for rendering input components
"""
import streamlit as st
from datetime import date, datetime
from typing import Dict

def render_defendant_info(case_data: Dict):
    """Render defendant information form"""
    st.header("👤 Defendant Information")
    
    # Name fields
    col1, col2, col3 = st.columns(3)
    with col1:
        case_data['last_name'] = st.text_input(
            "Last Name",
            value=case_data.get('last_name', ''),
            key="last_name"
        )
    
    with col2:
        case_data['first_name'] = st.text_input(
            "First Name",
            value=case_data.get('first_name', ''),
            key="first_name"
        )
    
    with col3:
        case_data['middle_name'] = st.text_input(
            "Middle Name",
            value=case_data.get('middle_name', ''),
            key="middle_name"
        )
    
    # DOB
    dob_value = case_data.get('dob')
    if dob_value:
        try:
            if isinstance(dob_value, str):
                dob_value = datetime.fromisoformat(dob_value).date()
        except:
            dob_value = None
    
    case_data['dob'] = st.date_input(
        "Date of Birth",
        value=dob_value,
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        key="dob"
    )
    
    # Address
    st.subheader("📍 Address")
    case_data['address'] = st.text_input(
        "Street Address",
        value=case_data.get('address', ''),
        key="address"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        case_data['city'] = st.text_input(
            "City",
            value=case_data.get('city', ''),
            key="city"
        )
    
    with col2:
        case_data['state'] = st.text_input(
            "State",
            value=case_data.get('state', 'FL'),
            key="state"
        )
    
    with col3:
        case_data['zip_code'] = st.text_input(
            "Zip Code",
            value=case_data.get('zip_code', ''),
            key="zip_code"
        )
    
    # Contact Information
    st.subheader("📞 Contact Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        case_data['phone_home'] = st.text_input(
            "Home Phone",
            value=case_data.get('phone_home', ''),
            key="phone_home"
        )
    
    with col2:
        case_data['phone_cell'] = st.text_input(
            "Cell Phone",
            value=case_data.get('phone_cell', ''),
            key="phone_cell"
        )
    
    with col3:
        case_data['phone_other'] = st.text_input(
            "Other Phone",
            value=case_data.get('phone_other', ''),
            key="phone_other"
        )
    
    # Status Information
    st.subheader("📊 Status Information")
    col1, col2 = st.columns(2)
    
    with col1:
        case_data['in_custody'] = st.checkbox(
            "Defendant in Custody",
            value=case_data.get('in_custody', False),
            key="in_custody"
        )
        
        case_data['on_probation'] = st.checkbox(
            "On Probation/Parole",
            value=case_data.get('on_probation', False),
            key="on_probation"
        )
        
        case_data['pending_charges'] = st.checkbox(
            "Pending Charges",
            value=case_data.get('pending_charges', False),
            key="pending_charges"
        )
    
    with col2:
        case_data['veteran'] = st.checkbox(
            "Veteran",
            value=case_data.get('veteran', False),
            key="veteran"
        )
        
        case_data['mental_health_issues'] = st.checkbox(
            "Mental Health Issues",
            value=case_data.get('mental_health_issues', False),
            key="mental_health_issues"
        )
        
        case_data['physical_disabilities'] = st.checkbox(
            "Physical Disabilities",
            value=case_data.get('physical_disabilities', False),
            key="physical_disabilities"
        )
    
    # Immigration Status
    case_data['immigration_status'] = st.text_input(
        "Immigration Status",
        value=case_data.get('immigration_status', ''),
        key="immigration_status"
    )
    
    # Comments
    case_data['defendant_comments'] = st.text_area(
        "Comments",
        value=case_data.get('defendant_comments', ''),
        key="defendant_comments",
        height=100
    )

def render_case_info(case_data: Dict):
    """Render case information form"""
    st.header("📋 Case Details")
    
    # Basic case info
    col1, col2 = st.columns(2)
    
    with col1:
        case_data['case_number'] = st.text_input(
            "Case Number",
            value=case_data.get('case_number', ''),
            key="case_number"
        )
        
        case_data['page_number'] = st.text_input(
            "Page Number",
            value=case_data.get('page_number', ''),
            key="page_number"
        )
    
    with col2:
        applied_date = case_data.get('applied_date')
        if applied_date and isinstance(applied_date, str):
            try:
                applied_date = datetime.fromisoformat(applied_date).date()
            except:
                applied_date = None
        
        case_data['applied_date'] = st.date_input(
            "Applied Date",
            value=applied_date,
            key="applied_date"
        )
        
        appointed_date = case_data.get('appointed_date')
        if appointed_date and isinstance(appointed_date, str):
            try:
                appointed_date = datetime.fromisoformat(appointed_date).date()
            except:
                appointed_date = None
        
        case_data['appointed_date'] = st.date_input(
            "Appointed Date",
            value=appointed_date,
            key="appointed_date"
        )
    
    # Case type
    case_data['case_type'] = st.selectbox(
        "Case Type",
        options=["Felony", "Misdemeanor", "Felony and/or MM", "Other"],
        index=["Felony", "Misdemeanor", "Felony and/or MM", "Other"].index(
            case_data.get('case_type', 'Felony and/or MM')
        ),
        key="case_type"
    )
    
    # Charges
    case_data['charges'] = st.text_area(
        "Charges",
        value=case_data.get('charges', ''),
        key="charges",
        height=100,
        help="Enter all charges, one per line if multiple"
    )
    
    # Prosecution info
    st.subheader("⚖️ Prosecution Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        case_data['asa'] = st.text_input(
            "ASA (Assistant State Attorney)",
            value=case_data.get('asa', ''),
            key="asa"
        )
    
    with col2:
        case_data['score'] = st.text_input(
            "Score",
            value=case_data.get('score', ''),
            key="score"
        )
    
    with col3:
        case_data['offer'] = st.text_input(
            "Offer",
            value=case_data.get('offer', ''),
            key="offer"
        )
    
    # Attorney assignment
    case_data['attorney'] = st.text_input(
        "Assigned Attorney",
        value=case_data.get('attorney', ''),
        key="attorney"
    )

def render_court_info(case_data: Dict):
    """Render court information form"""
    st.header("🏛️ Court Information")
    
    # Court division
    case_data['division'] = st.text_input(
        "Division",
        value=case_data.get('division', ''),
        key="division"
    )
    
    # Next court date and time
    col1, col2 = st.columns(2)
    
    with col1:
        court_date = case_data.get('court_date')
        if court_date and isinstance(court_date, str):
            try:
                court_date = datetime.fromisoformat(court_date).date()
            except:
                court_date = None
        
        case_data['court_date'] = st.date_input(
            "Next Court Date",
            value=court_date,
            key="court_date"
        )
    
    with col2:
        court_time = case_data.get('court_time', '')
        if isinstance(court_time, datetime):
            court_time = court_time.strftime("%H:%M")
        
        case_data['court_time'] = st.time_input(
            "Court Time",
            value=datetime.strptime(court_time, "%H:%M").time() if court_time else None,
            key="court_time"
        )
    
    # Court actions
    st.subheader("📅 Court Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        case_data['case_dispo'] = st.checkbox(
            "Case Disposition",
            value=case_data.get('case_dispo', False),
            key="case_dispo"
        )
        
        case_data['status_check'] = st.checkbox(
            "Status Check",
            value=case_data.get('status_check', False),
            key="status_check"
        )
        
        case_data['cal_call'] = st.checkbox(
            "Calendar Call",
            value=case_data.get('cal_call', False),
            key="cal_call"
        )
    
    with col2:
        case_data['non_jury_trial'] = st.checkbox(
            "Non-Jury Trial",
            value=case_data.get('non_jury_trial', False),
            key="non_jury_trial"
        )
        
        case_data['jury_trial'] = st.checkbox(
            "Jury Trial",
            value=case_data.get('jury_trial', False),
            key="jury_trial"
        )
        
        case_data['sentencing'] = st.checkbox(
            "Sentencing",
            value=case_data.get('sentencing', False),
            key="sentencing"
        )
    
    # Other court action
    case_data['other_court_action'] = st.text_input(
        "Other Court Action",
        value=case_data.get('other_court_action', ''),
        key="other_court_action"
    )
    
    # Reset reason
    case_data['reset_reason'] = st.text_area(
        "Reset Because",
        value=case_data.get('reset_reason', ''),
        key="reset_reason",
        height=100
    )
    
    # Disposition/Sentence
    st.subheader("📝 Disposition/Sentence")
    case_data['disposition_sentence'] = st.text_area(
        "Disposition/Sentence Details",
        value=case_data.get('disposition_sentence', ''),
        key="disposition_sentence",
        height=150
    )