from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_pradyumna_style_template(story, data, use_custom_font=False):
    # --- FONT & STYLE SETUP ---
    base_font = 'Times-Roman'
    bold_font = 'Times-Bold'

    styles = getSampleStyleSheet()
    # --- FONT SIZE & STYLE REFINEMENTS ---
    styles.add(ParagraphStyle(name='Name', fontName=bold_font, fontSize=16, alignment=TA_CENTER, spaceAfter=6, textColor=colors.black,borderPadding=2))
    styles.add(ParagraphStyle(name='ContactInfo', fontName=base_font, fontSize=9, alignment=TA_CENTER, spaceAfter=8))
    styles.add(ParagraphStyle(name='SectionHeader', fontName=bold_font, fontSize=12, spaceAfter=-2, textColor=colors.HexColor("#000001"), alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Body', fontName=base_font, fontSize=10, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='SkillsBody', fontName=base_font, fontSize=10, leading=15, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='ProjectTitle', parent=styles['Body'], spaceAfter=2, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Institution', fontName=bold_font, fontSize=10, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='EduDates', fontName=base_font, fontSize=10, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Degree', fontName=base_font, fontSize=10, leading=11, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Grade', fontName=base_font, fontSize=10, leading=11, alignment=TA_RIGHT))
    bullet_style = ParagraphStyle(name='Bullet', parent=styles['Normal'], fontName=base_font, fontSize=10, leftIndent=12, spaceBefore=0, leading=11, alignment=TA_LEFT)
    
    separator_line = Table([['']], colWidths=['100%'], style=[('LINEBELOW', (0,0), (-1,-1), 0.3, colors.darkgrey), ('TOPPADDING', (0,0), (-1,-1), 0)])

    # --- HEADER ---
    story.append(Paragraph(data.get('name', '').upper(), styles['Name']))

    # --- Build compact contact info line ---
    contact_parts = []
    if data.get('email'): contact_parts.append(data.get('email'))
    if data.get('linkedin'): contact_parts.append(f'<a href="{data.get("linkedin")}" color="black">LinkedIn</a>')
    if data.get('github'): contact_parts.append(f'<a href="{data.get("github")}" color="black">GitHub</a>')
    if data.get('leetcode'): contact_parts.append(f'<a href="{data.get("leetcode")}" color="black">LeetCode</a>')
    if data.get('phone'): contact_parts.append(data.get('phone'))
    
    contact_line = " &nbsp;|&nbsp; ".join(contact_parts)
    story.append(Paragraph(contact_line, styles['ContactInfo']))

    # --- SECTION BUILDER ---
    def add_section(title, content_generator):
        story.append(Spacer(1, 8))
        story.append(Paragraph(title, styles['SectionHeader']))
        story.append(separator_line)
        story.append(Spacer(1, 6))
        content_generator()

    # --- DYNAMIC SECTIONS ---
    if data.get('summary'):
        add_section("Summary", lambda: story.append(Paragraph(data.get('summary', ''), styles['Body'])))
        
    if data.get('education'):
        def education_content():
            for edu in data.get('education', []):
                grade_type = edu.get('grade_type', '')
                grade_value = edu.get('grade_value', '')
                grade_text = ""
                if grade_type and grade_value:
                    grade_text = f"<b>{grade_type}</b>: {grade_value}"

                table_data = [[Paragraph(edu.get('institution', ''), styles['Institution']), Paragraph(edu.get('dates', ''), styles['EduDates'])],
                              [Paragraph(edu.get('degree', ''), styles['Degree']), Paragraph(grade_text, styles['Grade'])]]
                tbl = Table(table_data, colWidths=['75%', '25%'])
                tbl.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,1), (-1,-1), 4)]))
                story.append(tbl)
        add_section("Education", education_content)

    if data.get('projects'):
        def projects_content():
            for project in data.get('projects', []):
                full_title = project.get('title', '')
                title_parts = full_title.split(':', 1)
                
                if len(title_parts) > 1:
                    main_title, subtitle = title_parts[0].strip(), title_parts[1].strip()
                    formatted_title = f"<b>{main_title}:</b> {subtitle}"
                    link_display_text = main_title
                else:
                    formatted_title = f"<b>{full_title}</b>"
                    link_display_text = full_title
                
                story.append(Paragraph(formatted_title, styles['ProjectTitle']))
                
                for point in project.get('points', []): story.append(Paragraph(f"• {point}", bullet_style))
                
                if project.get('techStack'):
                    story.append(Paragraph(f"<b>Technologies:</b> {project.get('techStack')}", bullet_style))
                
                if project.get('repo_link'):
                    story.append(Paragraph(f'<a href="{project.get("repo_link")}" color="black">GitHub: {link_display_text}</a>', bullet_style))
                
                story.append(Spacer(1, 10))
        add_section("Projects", projects_content)

    if data.get('skills'):
        add_section("Skills", lambda: story.append(Paragraph("".join([f"<b>{s.get('category')}:</b> {s.get('details')}<br/>" for s in data.get('skills', [])]), styles['SkillsBody'])))

    def experience_renderer(experience_list):
        for item in experience_list:
            header = f"<b>{item.get('role', '')}</b> | {item.get('company', '')} | <i>{item.get('dates', '')}</i>"
            story.append(Paragraph(header, styles['Body']))
            for point in item.get('responsibilities', []): story.append(Paragraph(f"• {point}", bullet_style))
            story.append(Spacer(1, 8))

    if data.get('internships'):
        add_section("Internship Experience", lambda: experience_renderer(data.get('internships')))
        
    if data.get('experience'):
        add_section("Work Experience", lambda: experience_renderer(data.get('experience')))

    if data.get('achievements'):
        add_section("Achievements", lambda: [story.append(Paragraph(f"• {ach}", bullet_style)) for ach in data.get('achievements')])

    if data.get('leadership'):
        add_section("Activities & Leadership", lambda: [story.append(Paragraph(f"• {act}", bullet_style)) for act in data.get('leadership')])

