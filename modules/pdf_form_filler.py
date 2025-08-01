"""
PDF Form Filler module for filling the official Case Opening Sheet PDF
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from typing import Dict
from datetime import datetime
import io


def fill_official_form(case_data: Dict, template_path: str = "CASE OPENING SHEET.pdf") -> str:
    """Fill the official Case Opening Sheet PDF form with case data"""
    
    # Create output filename
    defendant_name = f"{case_data.get('last_name', 'Unknown')}_{case_data.get('first_name', '')}"
    case_number = case_data.get('case_number', 'no_case_number').replace('/', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"exports/pdfs/{defendant_name}_{case_number}_official_{timestamp}.pdf"
    
    # Ensure output directory exists
    Path("exports/pdfs").mkdir(parents=True, exist_ok=True)
    
    # Read the template PDF
    template_pdf = PdfReader(template_path)
    output_pdf = PdfWriter()
    
    # Create a new PDF with the form data
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Set font
    can.setFont("Helvetica", 10)
    
    # Header row
    # Date
    if case_data.get('court_date'):
        court_date = case_data['court_date']
        if hasattr(court_date, 'strftime'):
            court_date = court_date.strftime('%m/%d/%Y')
        can.drawString(50, 735, court_date)
    
    # Page number
    if case_data.get('page_number'):
        can.drawString(362, 735, case_data['page_number'])
    
    # Applied date
    if case_data.get('applied_date'):
        applied_date = case_data['applied_date']
        if hasattr(applied_date, 'strftime'):
            applied_date = applied_date.strftime('%m/%d/%Y')
        can.drawString(445, 735, applied_date[:10])  # Limit length
    
    # Appointed date
    if case_data.get('appointed_date'):
        appointed_date = case_data['appointed_date']
        if hasattr(appointed_date, 'strftime'):
            appointed_date = appointed_date.strftime('%m/%d/%Y')
        can.drawString(540, 735, appointed_date[:10])  # Limit length
    
    # ASA line
    if case_data.get('asa'):
        can.drawString(60, 710, case_data['asa'][:20])  # Limit to prevent overflow
    
    # Score
    if case_data.get('score'):
        can.drawString(235, 710, case_data['score'][:15])
    
    # Offer
    if case_data.get('offer'):
        can.drawString(385, 710, case_data['offer'][:25])
    
    # Name fields
    if case_data.get('last_name'):
        can.drawString(130, 640, case_data['last_name'][:20])
    
    if case_data.get('first_name'):
        can.drawString(280, 640, case_data['first_name'][:15])
    
    if case_data.get('middle_name'):
        can.drawString(420, 640, case_data['middle_name'][:15])
    
    # DOB
    if case_data.get('dob'):
        dob = case_data['dob']
        if hasattr(dob, 'strftime'):
            dob = dob.strftime('%m/%d/%Y')
        can.drawString(515, 640, dob)
    
    # Address
    if case_data.get('address'):
        can.drawString(95, 610, case_data['address'][:60])
    
    # City, State, Zip
    if case_data.get('city'):
        can.drawString(60, 580, case_data['city'][:20])
    
    if case_data.get('state'):
        can.drawString(260, 580, case_data['state'][:2])
    
    if case_data.get('zip_code'):
        can.drawString(380, 580, case_data['zip_code'][:10])
    
    # Phone numbers
    if case_data.get('phone_home'):
        can.drawString(110, 550, case_data['phone_home'][:15])
    
    if case_data.get('phone_cell'):
        can.drawString(280, 550, case_data['phone_cell'][:15])
    
    if case_data.get('phone_other'):
        can.drawString(450, 550, case_data['phone_other'][:15])
    
    # Court information box
    # Court Date
    if case_data.get('court_date'):
        court_date = case_data['court_date']
        if hasattr(court_date, 'strftime'):
            court_date = court_date.strftime('%m/%d/%Y')
        can.drawString(155, 485, court_date)
    
    # Time
    if case_data.get('court_time'):
        court_time = case_data['court_time']
        if hasattr(court_time, 'strftime'):
            court_time = court_time.strftime('%I:%M %p')
        can.drawString(130, 460, court_time)
    
    # Division
    if case_data.get('division'):
        can.drawString(155, 435, case_data['division'][:15])
    
    # Checkboxes - use 'X' for checked items
    checkbox_y = 485
    if case_data.get('case_dispo'):
        can.drawString(480, checkbox_y, "X")
    
    if case_data.get('status_check'):
        can.drawString(630, checkbox_y, "X")
    
    checkbox_y = 460
    if case_data.get('cal_call'):
        can.drawString(365, checkbox_y, "X")
    
    if case_data.get('non_jury_trial'):
        can.drawString(520, checkbox_y, "X")
    
    if case_data.get('jury_trial'):
        can.drawString(365, checkbox_y - 25, "X")
    
    if case_data.get('sentencing'):
        can.drawString(520, checkbox_y - 25, "X")
    
    # Other court action
    if case_data.get('other_court_action'):
        can.drawString(360, checkbox_y - 50, case_data['other_court_action'][:20])
    
    # Status checkboxes (left side box)
    if case_data.get('on_probation'):
        can.drawString(370, 395, "X")
    else:
        can.drawString(325, 395, "X")
    
    if case_data.get('in_custody'):
        can.drawString(315, 375, "X")
    else:
        can.drawString(270, 375, "X")
    
    if case_data.get('veteran'):
        can.drawString(215, 340, "X")
    else:
        can.drawString(170, 340, "X")
    
    # Pending charges
    if case_data.get('pending_charges'):
        can.drawString(625, 395, "X")
    else:
        can.drawString(580, 395, "X")
    
    # Immigration status
    if case_data.get('immigration_status'):
        can.drawString(200, 355, case_data['immigration_status'][:15])
    
    # Mental health issues
    if case_data.get('mental_health_issues'):
        can.drawString(180, 305, "Mental health issues noted")
    
    # Physical disabilities  
    if case_data.get('physical_disabilities'):
        can.drawString(320, 290, "X")
    else:
        can.drawString(260, 290, "X")
    
    # Comments (limited to prevent overflow)
    if case_data.get('defendant_comments'):
        comments = case_data['defendant_comments']
        # Split into lines if needed
        lines = comments.split('\n')
        y_pos = 260
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            if i < 3 and y_pos > 220:
                can.drawString(120, y_pos, line[:70])
                y_pos -= 15
    
    # Case number
    if case_data.get('case_number'):
        can.drawString(140, 180, case_data['case_number'][:30])
    
    # Charges
    if case_data.get('charges'):
        charges = case_data['charges']
        lines = charges.split('\n')
        y_pos = 180
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            if i < 3:
                can.drawString(480, y_pos, line[:30])
                y_pos -= 20
    
    # Disposition/Sentence
    if case_data.get('disposition_sentence'):
        disposition = case_data['disposition_sentence']
        # Limit to one line to prevent overflow
        can.drawString(380, 100, disposition[:40])
    
    # Attorney
    if case_data.get('attorney'):
        can.drawString(165, 70, case_data['attorney'][:20])
    
    # Reset reason
    if case_data.get('reset_reason'):
        can.drawString(420, 70, case_data['reset_reason'][:35])
    
    # Save the overlay
    can.save()
    
    # Move to the beginning of the BytesIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    
    # Add the overlay to the template
    page = template_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output_pdf.add_page(page)
    
    # Write the output PDF
    with open(output_filename, "wb") as output_file:
        output_pdf.write(output_file)
    
    return output_filename