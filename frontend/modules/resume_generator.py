from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4 
from templates.template1 import create_pradyumna_style_template
from reportlab.pdfbase.ttfonts import TTFont

def generate_pdf(resume_data, output_path="output/resume.pdf"):
    """
    Generates a PDF resume using ReportLab and a specified template function.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           topMargin=40, bottomMargin=40,
                           leftMargin=40, rightMargin=40)

    try:
        pdfmetrics.registerFont(TTFont('Roboto', 'assets/fonts/Roboto-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Roboto-Bold', 'assets/fonts/Roboto-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('Roboto-Italic', 'assets/fonts/Roboto-Italic.ttf'))
        pdfmetrics.registerFontFamily('Roboto', normal='Roboto', bold='Roboto-Bold', italic='Roboto-Italic', boldItalic=None) # boldItalic not needed for this resume
        font_registered = True
    except Exception as e:
        print(f"Font Registration Error: {e}. Falling back to default fonts.")
        font_registered = False
    
    story = []
    
    create_pradyumna_style_template(story, resume_data, use_custom_font=font_registered)
    
    doc.build(story)
    print(f"PDF saved to {output_path}")
    return output_path