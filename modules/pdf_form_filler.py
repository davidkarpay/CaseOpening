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
    can.setFont("Helvetica", 9)
    
    # Header row - Top of page
    # Date (after "Date:")
    if case_data.get('court_date'):
        court_date = case_data['court_date']
        if hasattr(court_date, 'strftime'):
            court_date = court_date.strftime('%m/%d/%Y')
        can.drawString(90, 750, court_date)
    
    # Page number (after "Page:")
    if case_data.get('page_number'):
        can.drawString(340, 750, case_data['page_number'])
    
    # Applied date (after "Applied:")
    if case_data.get('applied_date'):
        applied_date = case_data['applied_date']
        if hasattr(applied_date, 'strftime'):
            applied_date = applied_date.strftime('%m/%d/%Y')
        can.drawString(420, 750, applied_date[:10])
    
    # Appointed date (after "Appointed:")
    if case_data.get('appointed_date'):
        appointed_date = case_data['appointed_date']
        if hasattr(appointed_date, 'strftime'):
            appointed_date = appointed_date.strftime('%m/%d/%Y')
        can.drawString(530, 750, appointed_date[:10])
    
    # Second line - ASA/Score/Offer
    # ASA (after "ASA:")
    if case_data.get('asa'):
        can.drawString(90, 730, case_data['asa'][:18])
    
    # Score (after "Score:")
    if case_data.get('score'):
        can.drawString(270, 730, case_data['score'][:15])
    
    # Offer (after "Offer:")
    if case_data.get('offer'):
        can.drawString(420, 730, case_data['offer'][:25])
    
    # Name section - under "Name" header
    # Last Name
    if case_data.get('last_name'):
        can.drawString(100, 650, case_data['last_name'][:15])
    
    # First Name
    if case_data.get('first_name'):
        can.drawString(240, 650, case_data['first_name'][:12])
    
    # Middle Name
    if case_data.get('middle_name'):
        can.drawString(380, 650, case_data['middle_name'][:10])
    
    # DOB (Date of Birth)
    if case_data.get('dob'):
        dob = case_data['dob']
        if hasattr(dob, 'strftime'):
            dob = dob.strftime('%m/%d/%Y')
        can.drawString(480, 650, dob)
    
    # Address (after "Address:")
    if case_data.get('address'):
        can.drawString(120, 620, case_data['address'][:45])
    
    # City, State, Zip line
    if case_data.get('city'):
        can.drawString(60, 590, case_data['city'][:18])
    
    if case_data.get('state'):
        can.drawString(240, 590, case_data['state'][:2])
    
    if case_data.get('zip_code'):
        can.drawString(350, 590, case_data['zip_code'][:10])
    
    # Phone section
    # Home Phone
    if case_data.get('phone_home'):
        can.drawString(80, 560, case_data['phone_home'][:12])
    
    # Cell Phone  
    if case_data.get('phone_cell'):
        can.drawString(220, 560, case_data['phone_cell'][:12])
    
    # Other Phone
    if case_data.get('phone_other'):
        can.drawString(380, 560, case_data['phone_other'][:12])
    
    # Court information box (Next Court Action & Intake Info)
    # Court Date (after "Court Date:")
    if case_data.get('court_date'):
        court_date = case_data['court_date']
        if hasattr(court_date, 'strftime'):
            court_date = court_date.strftime('%m/%d/%Y')
        can.drawString(140, 495, court_date)
    
    # Time (after "Time:")
    if case_data.get('court_time'):
        court_time = case_data['court_time']
        if hasattr(court_time, 'strftime'):
            court_time = court_time.strftime('%I:%M %p')
        can.drawString(110, 475, court_time)
    
    # Division (after "Division:")
    if case_data.get('division'):
        can.drawString(140, 455, case_data['division'][:12])
    
    # Right side checkboxes in the court box
    # Case Dispo checkbox
    if case_data.get('case_dispo'):
        can.drawString(495, 495, "X")
    
    # Status Check checkbox  
    if case_data.get('status_check'):
        can.drawString(575, 495, "X")
    
    # Cal Call checkbox
    if case_data.get('cal_call'):
        can.drawString(420, 475, "X")
    
    # Non Jury Trial checkbox
    if case_data.get('non_jury_trial'):
        can.drawString(500, 475, "X")
    
    # Jury Trial checkbox
    if case_data.get('jury_trial'):
        can.drawString(420, 455, "X")
    
    # Sentencing checkbox
    if case_data.get('sentencing'):
        can.drawString(500, 455, "X")
    
    # Other court action (after "Other:")
    if case_data.get('other_court_action'):
        can.drawString(420, 435, case_data['other_court_action'][:18])
    
    # Status checkboxes (bottom section)
    # Defendant on Probation/Parole
    if case_data.get('on_probation'):
        can.drawString(385, 415, "X")  # Yes checkbox
    else:
        can.drawString(360, 415, "X")  # No checkbox
    
    # Pending Charges  
    if case_data.get('pending_charges'):
        can.drawString(570, 415, "X")  # Yes checkbox
    else:
        can.drawString(545, 415, "X")  # No checkbox
    
    # Defendant in Custody
    if case_data.get('in_custody'):
        can.drawString(385, 395, "X")  # Yes checkbox
    else:
        can.drawString(360, 395, "X")  # No checkbox
    
    # Immigration Status (after "Immigration Status:")
    if case_data.get('immigration_status'):
        can.drawString(220, 375, case_data['immigration_status'][:12])
    
    # Veteran
    if case_data.get('veteran'):
        can.drawString(220, 355, "X")  # Yes checkbox
    else:
        can.drawString(195, 355, "X")  # No checkbox
    
    # Case type - Felony and/or MM (this appears to be pre-printed)
    
    # Mental Health Issues (text field)
    if case_data.get('mental_health_issues'):
        can.drawString(160, 315, "Issues noted")
    
    # Physical disabilities  
    if case_data.get('physical_disabilities'):
        can.drawString(320, 295, "X")  # Yes checkbox
    else:
        can.drawString(295, 295, "X")  # No checkbox
    
    # Comments section (after "Comments:")
    if case_data.get('defendant_comments'):
        comments = case_data['defendant_comments']
        # Split into lines to fit in the space
        lines = comments.split('\n')
        y_pos = 270
        for i, line in enumerate(lines[:2]):  # Max 2 lines to fit
            if y_pos > 250:
                can.drawString(120, y_pos, line[:65])
                y_pos -= 12
    
    # Case number (after "Case No.:")
    if case_data.get('case_number'):
        can.drawString(120, 220, case_data['case_number'][:25])
    
    # Charges (after "Charge")
    if case_data.get('charges'):
        charges = case_data['charges']
        lines = charges.split('\n')
        y_pos = 220
        for i, line in enumerate(lines[:3]):  # Max 3 lines
            if y_pos > 200:
                can.drawString(420, y_pos, line[:25])
                y_pos -= 12
    
    # Disposition/Sentence (after "DISPOSITION/SENTENCE")
    if case_data.get('disposition_sentence'):
        disposition = case_data['disposition_sentence']
        can.drawString(400, 120, disposition[:35])
    
    # Attorney (after "ATTORNEY:")
    if case_data.get('attorney'):
        can.drawString(120, 90, case_data['attorney'][:18])
    
    # Reset reason (after "Reset Because:")
    if case_data.get('reset_reason'):
        can.drawString(390, 90, case_data['reset_reason'][:30])
    
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