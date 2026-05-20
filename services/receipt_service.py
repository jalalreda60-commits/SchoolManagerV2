import os
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPTS_DIR = os.path.join(BASE_DIR, 'receipts')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


def generate_receipt_pdf(receipt_data: dict) -> str:
    """Generate a PDF receipt and return the file path."""
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    
    receipt_number = receipt_data.get('receipt_number', 'REC-0000')
    filename = f"{receipt_number}.pdf"
    filepath = os.path.join(RECEIPTS_DIR, filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Colors
    primary = colors.HexColor('#FF6B00')
    dark = colors.HexColor('#1a1a2e')
    light_bg = colors.HexColor('#FFF5EE')
    
    # Header with logo
    logo_path = os.path.join(ASSETS_DIR, 'school_logo.png')
    
    header_data = []
    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=40*mm, height=40*mm)
        header_data.append([logo, '', ''])
    
    # School info style
    school_style = ParagraphStyle('school', fontSize=16, fontName='Helvetica-Bold',
                                   textColor=primary, alignment=TA_CENTER)
    sub_style = ParagraphStyle('sub', fontSize=9, fontName='Helvetica',
                                textColor=colors.grey, alignment=TA_CENTER)
    title_style = ParagraphStyle('title', fontSize=20, fontName='Helvetica-Bold',
                                  textColor=dark, alignment=TA_CENTER)
    label_style = ParagraphStyle('label', fontSize=9, fontName='Helvetica-Bold',
                                  textColor=colors.grey)
    value_style = ParagraphStyle('value', fontSize=11, fontName='Helvetica-Bold',
                                  textColor=dark)
    
    school_name = receipt_data.get('school_name', 'Le Schéma')
    school_address = receipt_data.get('school_address', 'Maroc')
    school_phone = receipt_data.get('school_phone', '')
    
    # Header table
    if os.path.exists(logo_path):
        logo_img = RLImage(logo_path, width=35*mm, height=35*mm)
        school_block = Paragraph(f"<b>{school_name}</b>", school_style)
        sub_block = Paragraph(f"{school_address}<br/>{school_phone}", sub_style)
        rec_title = Paragraph("REÇU DE PAIEMENT", title_style)
        rec_num = Paragraph(f"<b>{receipt_number}</b>", 
                           ParagraphStyle('recnum', fontSize=12, textColor=primary, 
                                         fontName='Helvetica-Bold', alignment=TA_RIGHT))
        
        header_table = Table([
            [logo_img, school_block, rec_num],
            ['', sub_block, ''],
        ], colWidths=[45*mm, 100*mm, 45*mm])
    else:
        school_block = Paragraph(f"<b>{school_name}</b>", school_style)
        rec_num = Paragraph(f"<b>{receipt_number}</b>",
                           ParagraphStyle('recnum', fontSize=12, textColor=primary,
                                         fontName='Helvetica-Bold', alignment=TA_RIGHT))
        header_table = Table([[school_block, rec_num]], colWidths=[120*mm, 60*mm])
    
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 5*mm))
    
    # Divider
    divider = Table([['']], colWidths=[180*mm], rowHeights=[2])
    divider.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), primary),]))
    story.append(divider)
    story.append(Spacer(1, 5*mm))
    
    # Date and receipt info
    date_str = receipt_data.get('payment_date', datetime.now().strftime('%d/%m/%Y %H:%M'))
    info_table = Table([
        [Paragraph('Date:', label_style), Paragraph(str(date_str), value_style),
         Paragraph('Caissier:', label_style), Paragraph(receipt_data.get('cashier', 'Admin'), value_style)]
    ], colWidths=[25*mm, 65*mm, 30*mm, 60*mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 5*mm))
    
    # Student info box
    story.append(Paragraph("INFORMATIONS ÉLÈVE", 
                           ParagraphStyle('section', fontSize=10, fontName='Helvetica-Bold',
                                         textColor=primary)))
    story.append(Spacer(1, 2*mm))
    
    student_data = [
        [Paragraph('Nom complet:', label_style), 
         Paragraph(receipt_data.get('student_name', ''), value_style),
         Paragraph('Code élève:', label_style),
         Paragraph(receipt_data.get('student_code', ''), value_style)],
        [Paragraph('Classe:', label_style),
         Paragraph(receipt_data.get('class_name', ''), value_style),
         Paragraph('Parent:', label_style),
         Paragraph(receipt_data.get('parent_name', ''), value_style)],
    ]
    student_table = Table(student_data, colWidths=[30*mm, 65*mm, 25*mm, 60*mm])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [light_bg, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(student_table)
    story.append(Spacer(1, 5*mm))
    
    # Payment details
    story.append(Paragraph("DÉTAILS DU PAIEMENT",
                           ParagraphStyle('section', fontSize=10, fontName='Helvetica-Bold',
                                         textColor=primary)))
    story.append(Spacer(1, 2*mm))
    
    payment_type_map = {
        'monthly': 'Frais de scolarité mensuel',
        'insurance': 'Assurance annuelle',
        'transport': 'Frais de transport'
    }
    ptype = receipt_data.get('payment_type', 'monthly')
    ptype_label = payment_type_map.get(ptype, ptype)
    
    month_names = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    month_num = receipt_data.get('month', 0)
    month_label = month_names[month_num] if month_num else ''
    year_label = str(receipt_data.get('year', ''))
    period = f"{month_label} {year_label}".strip() if month_label else year_label
    
    currency = receipt_data.get('currency', 'MAD')
    amount = receipt_data.get('amount', 0)
    
    pay_rows = [
        [Paragraph('Désignation', ParagraphStyle('th', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white)),
         Paragraph('Période', ParagraphStyle('th', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white)),
         Paragraph('Montant', ParagraphStyle('th', fontSize=9, fontName='Helvetica-Bold', textColor=colors.white))],
        [Paragraph(ptype_label, value_style),
         Paragraph(period, value_style),
         Paragraph(f"{amount:,.2f} {currency}", 
                  ParagraphStyle('amount', fontSize=11, fontName='Helvetica-Bold', 
                                textColor=primary, alignment=TA_RIGHT))],
    ]
    pay_table = Table(pay_rows, colWidths=[90*mm, 50*mm, 40*mm])
    pay_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), dark),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('RIGHTPADDING', (2,0), (2,-1), 8),
    ]))
    story.append(pay_table)
    story.append(Spacer(1, 3*mm))
    
    # Total box
    total_table = Table([
        [Paragraph('TOTAL PAYÉ', ParagraphStyle('totallabel', fontSize=11, fontName='Helvetica-Bold',
                                                 textColor=colors.white, alignment=TA_RIGHT)),
         Paragraph(f"{amount:,.2f} {currency}",
                  ParagraphStyle('totalamt', fontSize=14, fontName='Helvetica-Bold',
                                textColor=colors.white, alignment=TA_RIGHT))]
    ], colWidths=[130*mm, 50*mm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (1,0), (1,0), 10),
        ('LEFTPADDING', (0,0), (0,0), 10),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 8*mm))
    
    # QR Code
    qr_data = f"RECU:{receipt_number}|ELEVE:{receipt_data.get('student_code','')}|MONTANT:{amount}|DATE:{date_str}"
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color='black', back_color='white')
    qr_path = os.path.join(RECEIPTS_DIR, f'qr_{receipt_number}.png')
    qr_img.save(qr_path)
    
    sig_style = ParagraphStyle('sig', fontSize=9, fontName='Helvetica',
                                textColor=colors.grey, alignment=TA_CENTER)
    
    qr_rl = RLImage(qr_path, width=25*mm, height=25*mm)
    bottom_table = Table([
        [Paragraph('Signature & Cachet', sig_style), '', qr_rl],
        [Paragraph('_______________________', sig_style), '', 
         Paragraph(f'Scan pour vérifier', sig_style)],
    ], colWidths=[70*mm, 70*mm, 40*mm])
    bottom_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(bottom_table)
    story.append(Spacer(1, 5*mm))
    
    # Footer
    footer_divider = Table([['']], colWidths=[180*mm], rowHeights=[1])
    footer_divider.setStyle(TableStyle([('BACKGROUND', (0,0), (0,0), colors.HexColor('#e0e0e0'))]))
    story.append(footer_divider)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"<i>Ce reçu est généré automatiquement par le système de gestion de {school_name}. "
        f"Conservez-le comme preuve de paiement.</i>",
        ParagraphStyle('footer', fontSize=7, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    doc.build(story)
    
    # Cleanup QR temp file
    if os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except:
            pass
    
    return filepath
