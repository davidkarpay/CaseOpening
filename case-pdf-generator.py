"""
PDF Generator module for creating case opening sheet PDFs
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
from typing import Dict

def generate_case_pdf(case_data: Dict) -> str:
    """Generate PDF from case data"""
    # Create filename
    defendant_name = f"{case_data.get('last_name', 'Unknown')}_{case_data.get('first_name', '')}"
    case_number = case_data.get('case_number', 'no_case_number').replace('/', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"exports/pdfs/{defendant_name}_{case_number}_{timestamp}.pdf"
    Path("exports/pdfs").mkdir(parents=True, exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2e86ab'),
        spaceAfter=6
    )
    
    # Build content
    content = []
    
    # Header
    header_data = [
        ['Date:', case_data.get('court_date', '__________'), 'Page:', case_data.get('page_number', '____')],
        ['Applied:', case_data.get('applied_date', '____'), 'Appointed:', case_data.get('appointed_date', '____')]
    ]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    content.append(header_table)
    content.append(Spacer(1, 0.2*inch))
    
    # ASA/Score/Offer line
    asa_data = [
        ['ASA:', case_data.get('asa', '________________'), 
         'Score:', case_data.get('score', '________________'),
         'Offer:', case_data.get('offer', '________________')]
    ]
    
    asa_table = Table(asa_data, colWidths=[0.5*inch, 2.5*inch, 0.5*inch, 1.5*inch, 0.5*inch, 2*inch])
    asa_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    content.append(asa_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Title
    content.append(Paragraph("OFFICE OF THE PUBLIC DEFENDER", title_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Defendant Name and DOB
    name = f"{case_data.get('last_name', '')} {case_data.get('first_name', '')} {case_data.get('middle_name', '')}"
    dob = case_data.get('dob', '')
    if hasattr(dob, 'strftime'):
        dob = dob.strftime('%m/%d/%Y')
    
    content.append(Paragraph(f"<b>Name:</b> {name.strip()}", styles['Normal']))
    content.append(Paragraph(f"<b>D.O.B.:</b> {dob}", styles['Normal']))
    content.append(Spacer(1, 0.1*inch))
    
    # Address
    address = case_data.get('address', '')
    city = case_data.get('city', '')
    state = case_data.get('state', '')
    zip_code = case_data.get('zip_code', '')
    
    content.append(Paragraph(f"<b>Address:</b> {address}", styles['Normal']))
    content.append(Paragraph(f"{city}, {state} {zip_code}", styles['Normal']))
    content.append(Spacer(1, 0.1*inch))
    
    # Phone
    phones = []
    if case_data.get('phone_home'):
        phones.append(f"Home: {case_data['phone_home']}")
    if case_data.get('phone_cell'):
        phones.append(f"Cell: {case_data['phone_cell']}")
    if case_data.get('phone_other'):
        phones.append(f"Other: {case_data['phone_other']}")
    
    content.append(Paragraph(f"<b>Phone:</b> {', '.join(phones)}", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    # Court Information
    content.append(Paragraph("<b>Next Court Action & Intake Info</b>", heading_style))
    
    court_info = []
    if case_data.get('court_date'):
        court_date = case_data['court_date']
        if hasattr(court_date, 'strftime'):
            court_date = court_date.strftime('%m/%d/%Y')
        court_info.append(f"Court Date: {court_date}")
    
    if case_data.get('court_time'):
        court_time = case_data['court_time']
        if hasattr(court_time, 'strftime'):
            court_time = court_time.strftime('%I:%M %p')
        court_info.append(f"Time: {court_time}")
    
    if case_data.get('division'):
        court_info.append(f"Division: {case_data['division']}")
    
    # Court actions
    actions = []
    if case_data.get('case_dispo'):
        actions.append("Case Dispo")
    if case_data.get('status_check'):
        actions.append("Status Check")
    if case_data.get('cal_call'):
        actions.append("Cal Call")
    if case_data.get('non_jury_trial'):
        actions.append("Non Jury Trial")
    if case_data.get('jury_trial'):
        actions.append("Jury Trial")
    if case_data.get('sentencing'):
        actions.append("Sentencing")
    if case_data.get('other_court_action'):
        actions.append(f"Other: {case_data['other_court_action']}")
    
    if actions:
        court_info.append(f"Actions: {', '.join(actions)}")
    
    for info in court_info:
        content.append(Paragraph(info, styles['Normal']))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Status Information
    status_info = []
    if case_data.get('on_probation'):
        status_info.append("On Probation/Parole: Yes")
    if case_data.get('pending_charges'):
        status_info.append("Pending Charges: Yes")
    if case_data.get('in_custody'):
        status_info.append("In Custody: Yes")
    if case_data.get('veteran'):
        status_info.append("Veteran: Yes")
    if case_data.get('immigration_status'):
        status_info.append(f"Immigration Status: {case_data['immigration_status']}")
    if case_data.get('mental_health_issues'):
        status_info.append("Mental Health Issues: Yes")
    if case_data.get('physical_disabilities'):
        status_info.append("Physical Disabilities: Yes")
    
    for info in status_info:
        content.append(Paragraph(info, styles['Normal']))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Case Information
    content.append(Paragraph("<b>Case Information</b>", heading_style))
    
    if case_data.get('case_number'):
        content.append(Paragraph(f"Case No.: {case_data['case_number']}", styles['Normal']))
    
    if case_data.get('case_type'):
        content.append(Paragraph(f"Type: {case_data['case_type']}", styles['Normal']))
    
    if case_data.get('charges'):
        content.append(Paragraph(f"Charges: {case_data['charges']}", styles['Normal']))
    
    content.append(Spacer(1, 0.2*inch))
    
    # Comments
    if case_data.get('defendant_comments'):
        content.append(Paragraph("<b>Comments:</b>", heading_style))
        content.append(Paragraph(case_data['defendant_comments'], styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
    
    # Disposition/Sentence
    if case_data.get('disposition_sentence'):
        content.append(Paragraph("<b>DISPOSITION/SENTENCE:</b>", heading_style))
        content.append(Paragraph(case_data['disposition_sentence'], styles['Normal']))
        content.append(Spacer(1, 0.2*inch))
    
    # Attorney and Reset
    if case_data.get('attorney'):
        content.append(Paragraph(f"<b>ATTORNEY:</b> {case_data['attorney']}", styles['Normal']))
    
    if case_data.get('reset_reason'):
        content.append(Paragraph(f"<b>Reset Because:</b> {case_data['reset_reason']}", styles['Normal']))
    
    # Build PDF
    doc.build(content)
    
    return filename