"""
build_pdf_report.py
Generates the complete, publication-grade academic PDF project report using ReportLab.
Features custom two-pass page numbering:
- Roman numerals (ii, iii, iv, v, vi) for Front Matter
- Arabic numerals (1, 2, 3, ...) for Chapter 1 onwards
- Running headers and footers with decorative rules
"""

import os
import re
import html
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table,
    TableStyle, PageBreak, KeepTogether, Preformatted, HRFlowable
)
from reportlab.pdfgen import canvas

from report_content import (
    METADATA, DECLARATION_TEXT, SUPERVISOR_CONFIRMATION,
    CERTIFICATE_TEXT, ACKNOWLEDGEMENTS_TEXT, ABSTRACT_TEXT,
    KEYWORDS, ABBREVIATIONS, TABLES_DATA
)
from report_text import (
    CH1_INTRO, CH2_SRS, CH3_DESIGN, CH4_IMPL_RESULTS,
    CH5_CONCLUSION, REFERENCES_DATA
)
from appendix_code import (
    CODE_APP_PY, CODE_RESUME_PARSER, CODE_TEXT_PREPROCESSOR,
    CODE_SKILL_EXTRACTOR, CODE_JOB_ANALYZER, CODE_SKILL_MATCHER,
    CODE_GAP_DETECTOR, CODE_REQUIREMENTS_TXT, SAMPLE_TAXONOMY_JSON,
    SAMPLE_JOB_DESCRIPTION, SAMPLE_SYNTHETIC_RESUME, APP_B_TEXT
)

def int_to_roman(num):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
    roman_num = ""
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that determines page boundaries and draws appropriate
    headers and footers:
    - Page 1: Cover (blank header & footer)
    - Pages 2 to front_matter_end: Roman numerals (ii, iii, ...)
    - Main chapters: Arabic numerals (1, 2, 3, ...) with running top header
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.front_matter_pages = 5  # Pages 1 to 5 are front matter

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber
        self.saveState()
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.HexColor("#475569"))

        # Width and height of A4
        w, h = A4

        if page_num == 1:
            # Cover page - no header or footer
            self.restoreState()
            return

        if page_num <= self.front_matter_pages:
            # Front matter: Roman numerals
            roman = int_to_roman(page_num)
            self.drawCentredString(w / 2.0, 36, roman)
        else:
            # Main matter: Arabic numerals starting at 1 for Chapter 1
            arabic_page = page_num - self.front_matter_pages
            
            # Running Header
            self.drawString(54, h - 36, "AI-Based Resume Analysis and Skill Gap Detection")
            self.drawRightString(w - 54, h - 36, "BCA Project Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(54, h - 42, w - 54, h - 42)

            # Running Footer
            self.drawCentredString(w / 2.0, 36, str(arabic_page))
            self.line(54, 48, w - 54, 48)

        self.restoreState()

def build_pdf_document():
    pdf_path = os.path.join("bca_report_output", "BCA_Project_Report_Resume_Analysis.pdf")
    print(f"Compiling PDF report to: {pdf_path}")

    # Margins: 54pt = 0.75 in
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=20,
        leading=24,
        alignment=1, # Center
        textColor=colors.HexColor('#1B365D'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'ChapterHeading1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1B365D'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionHeading2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12.5,
        leading=15,
        textColor=colors.HexColor('#1E40AF'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SubSectionHeading3',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'AcademicBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=13.5,
        alignment=4, # Justified
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'AcademicBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9,
        leading=11,
        alignment=1, # Center
        textColor=colors.HexColor('#475569'),
        spaceBefore=3,
        spaceAfter=10
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A')
    )

    def clean_text_for_xml(txt):
        if not txt:
            return ""
        # Escape XML entities
        escaped = html.escape(txt)
        # Re-allow basic bold and italic tags if passed specifically
        return escaped

    def add_p(text, bold_prefix=None, is_bullet=False):
        c_text = clean_text_for_xml(text)
        if bold_prefix:
            c_prefix = clean_text_for_xml(bold_prefix)
            content = f"<b>{c_prefix}</b> {c_text}"
        else:
            content = c_text
        style = bullet_style if is_bullet else body_style
        return Paragraph(content, style)

    def make_table(headers, rows, col_widths):
        data = [[Paragraph(f"<b>{clean_text_for_xml(h)}</b>", ParagraphStyle('TH', parent=body_style, fontName='Times-Bold', fontSize=8.5, leading=10, textColor=colors.white)) for h in headers]]
        for r_idx, r in enumerate(rows):
            row_cells = []
            bg_col = colors.HexColor('#F8FAFC') if r_idx % 2 == 1 else colors.white
            for c in r:
                row_cells.append(Paragraph(clean_text_for_xml(str(c)), ParagraphStyle('TD', parent=body_style, fontSize=8, leading=10, textColor=colors.HexColor('#1F2937'))))
            data.append(row_cells)

        t = Table(data, colWidths=col_widths, repeatRows=1)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1B365D')),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]
        for r_idx in range(1, len(data)):
            bg = colors.HexColor('#F8FAFC') if r_idx % 2 == 0 else colors.white
            t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg))
        t.setStyle(TableStyle(t_style))
        return t

    story = []

    # -------------------------------------------------------------
    # 1. COVER PAGE
    # -------------------------------------------------------------
    story.append(Spacer(1, 20))
    story.append(Paragraph("A Project Report<br/>On", ParagraphStyle('Sub', parent=body_style, fontName='Times-Bold', fontSize=13, leading=16, alignment=1)))
    story.append(Spacer(1, 15))
    story.append(Paragraph(METADATA['title'], title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Submitted in partial fulfillment of the<br/>requirement for the award of the degree of", ParagraphStyle('Ital', parent=body_style, fontName='Times-Italic', fontSize=10.5, leading=14, alignment=1)))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>{METADATA['degree']}</b><br/>DEGREE<br/>{METADATA['session']}<br/>{METADATA['stream']}", ParagraphStyle('CenterBold', parent=body_style, fontName='Times-Bold', fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 25))
    story.append(Paragraph(f"By<br/><b>{METADATA['student_name']}</b> (Admission No. {METADATA['roll_no']})", ParagraphStyle('By', parent=body_style, fontName='Times-Roman', fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Under the guidance of<br/><b>{METADATA['guide_name']}</b><br/>{METADATA['guide_desig']}", ParagraphStyle('Guide', parent=body_style, fontName='Times-Roman', fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 45))
    story.append(Paragraph(f"<b>{METADATA['dept_name']}</b><br/><b>{METADATA['university_name']}, {METADATA['city']}</b><br/><b>{METADATA['country']}</b><br/><br/><b>{METADATA['submission_date']}</b>", ParagraphStyle('Dept', parent=body_style, fontName='Times-Bold', fontSize=10.5, leading=14, alignment=1, textColor=colors.HexColor('#1B365D'))))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 2. DECLARATION & CERTIFICATE (Page ii)
    # -------------------------------------------------------------
    story.append(Paragraph(f"<b>{METADATA['dept_name']}</b><br/><b>{METADATA['university_name']}, {METADATA['city']}</b>", ParagraphStyle('CenterBold', parent=body_style, fontName='Times-Bold', fontSize=10, leading=13, alignment=1)))
    story.append(Paragraph("CANDIDATE'S DECLARATION", h1_style))
    for para in DECLARATION_TEXT.split('\n\n'):
        story.append(add_p(para))

    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Student Name (Admission No.):</b><br/>{METADATA['student_name']} ({METADATA['roll_no']})", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{SUPERVISOR_CONFIRMATION}</i>", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Guide Name:</b> {METADATA['guide_name']}<br/><b>Designation:</b> {METADATA['guide_desig']}<br/><b>Signature:</b> ______________________     <b>Date:</b> ______________", body_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("CERTIFICATE", h1_style))
    story.append(add_p(CERTIFICATE_TEXT))
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "<b>Signature of Examiner(s)</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Signature of Supervisor(s)</b><br/>"
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;({METADATA['guide_name']})<br/>"
        f"<b>Date:</b> {METADATA['submission_date']}<br/>"
        f"<b>Place:</b> {METADATA['city']}", body_style
    ))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 3. ACKNOWLEDGEMENTS & ABSTRACT (Page iii)
    # -------------------------------------------------------------
    story.append(Paragraph("ACKNOWLEDGEMENTS", h1_style))
    for para in ACKNOWLEDGEMENTS_TEXT.split('\n\n'):
        story.append(add_p(para))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{METADATA['student_name']}</b><br/>Admission No: {METADATA['roll_no']}", body_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("ABSTRACT", h1_style))
    story.append(add_p(ABSTRACT_TEXT))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Keywords:</b> <i>{', '.join(KEYWORDS)}.</i>", body_style))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 4. TABLE OF CONTENTS (Page iv)
    # -------------------------------------------------------------
    story.append(Paragraph("TABLE OF CONTENTS", h1_style))
    toc_data = [
        ("DECLARATION", "ii"),
        ("CERTIFICATE", "ii"),
        ("ACKNOWLEDGEMENTS", "iii"),
        ("ABSTRACT", "iii"),
        ("CHAPTER 1   INTRODUCTION", "1"),
        ("    1.1 Problem Introduction", "1"),
        ("        1.1.1 Motivation", "1"),
        ("        1.1.2 Project Objectives", "1"),
        ("        1.1.3 Scope of the Project", "1"),
        ("    1.2 Related Previous Work", "2"),
        ("    1.3 Organization of the Report", "2"),
        ("CHAPTER 2   SOFTWARE REQUIREMENT SPECIFICATION", "3"),
        ("    2.1 Product Perspective", "3"),
        ("        2.1.1 System Interfaces", "3"),
        ("        2.1.2 User Interfaces", "3"),
        ("        2.1.3 Hardware Interfaces", "3"),
        ("        2.1.4 Software Interfaces", "3"),
        ("        2.1.5 Communications Interfaces", "3"),
        ("        2.1.6 Memory Constraints", "3"),
        ("        2.1.7 Operations", "3"),
        ("        2.1.8 Site Adaptation Requirements", "3"),
        ("    2.2 Product Functions", "3"),
        ("    2.3 User Characteristics", "4"),
        ("    2.4 Constraints", "4"),
        ("    2.5 Assumptions and Dependencies", "4"),
        ("    2.6 Apportioning of Requirements", "4"),
        ("    2.7 Use Case Model", "4"),
        ("CHAPTER 3   SYSTEM DESIGN", "7"),
        ("    3.1 Architecture Diagram", "7"),
        ("    3.2 Dataset and Training / Processing Pipeline", "7"),
        ("    3.3 Feature Design", "8"),
        ("    3.4 Module / Class Diagram", "8"),
        ("    3.5 Data Flow Diagrams", "9"),
        ("    3.6 Activity Diagram (Decision Flow)", "10"),
        ("    3.7 Data Storage and Schema", "10"),
        ("    3.8 Algorithms Used", "10"),
        ("CHAPTER 4   IMPLEMENTATION AND RESULTS", "11"),
        ("    4.1 Software and Hardware Requirements", "11"),
        ("    4.2 Assumptions and Dependencies", "11"),
        ("    4.3 Constraints", "11"),
        ("    4.4 Implementation Details", "11"),
        ("        4.4.1 Snapshots of Interfaces", "11"),
        ("        4.4.2 Test Cases", "12"),
        ("    4.5 Results and Evaluation", "12"),
        ("    4.6 Challenges and Lessons Learned", "14"),
        ("CHAPTER 5   CONCLUSION", "16"),
        ("    5.1 Performance Evaluation", "16"),
        ("    5.2 Comparison with Existing Approaches", "16"),
        ("    5.3 Future Directions", "16"),
        ("APPENDIX A   Important Source Code", "17"),
        ("    A.1 Flask Web Application (app.py)", "17"),
        ("    A.2 Document Text Stream Parser (resume_parser.py)", "18"),
        ("    A.3 Text Preprocessor & Sanitizer (text_preprocessor.py)", "18"),
        ("    A.4 Skill Extractor & Taxonomy Matcher (skill_extractor.py)", "19"),
        ("    A.5 Job Analyzer (job_analyzer.py)", "19"),
        ("    A.6 Skill Matcher & Scoring Engine (skill_matcher.py)", "20"),
        ("    A.7 Gap Detector & Upskilling Roadmap (gap_detector.py)", "20"),
        ("    A.8 Requirements Specification (requirements.txt)", "21"),
        ("    A.9 Curated Skills Taxonomy Snippet (skills_taxonomy.json)", "21"),
        ("    A.10 Sample Test Documents", "21"),
        ("APPENDIX B   How to Run the Project", "22"),
        ("    Folder Structure", "22"),
        ("    Execution Steps", "22"),
        ("REFERENCES", "23")
    ]
    t_toc_data = [[Paragraph(f"<b>{clean_text_for_xml(item[0])}</b>" if "CHAPTER" in item[0] or "APPENDIX" in item[0] or item[0] in ["DECLARATION", "CERTIFICATE", "ACKNOWLEDGEMENTS", "ABSTRACT", "REFERENCES"] else clean_text_for_xml(item[0]), ParagraphStyle('TOCItem', parent=body_style, fontSize=7.5, leading=9.5)),
                   Paragraph(item[1], ParagraphStyle('TOCPg', parent=body_style, fontSize=7.5, leading=9.5, alignment=2))] for item in toc_data]
    t_toc = Table([[Paragraph("<b>Section Title</b>", ParagraphStyle('TH', parent=body_style, fontName='Times-Bold', fontSize=8.5, textColor=colors.white)), Paragraph("<b>Page</b>", ParagraphStyle('TH2', parent=body_style, fontName='Times-Bold', fontSize=8.5, alignment=2, textColor=colors.white))]] + t_toc_data, colWidths=[410, 77])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B365D')),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor('#F1F5F9'))
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 5. LIST OF TABLES, FIGURES & ABBREVIATIONS (Page v)
    # -------------------------------------------------------------
    story.append(Paragraph("LIST OF TABLES", h2_style))
    tables_list = [
        ("Table 2.1", "Use case scenario - UC-01: Analyze Resume and Detect Skill Gaps", "5"),
        ("Table 3.1", "Curated Skill Taxonomy Domain Distribution and Sample Entities", "7"),
        ("Table 3.2", "Extracted Features and Profiles in the Resume Analysis System", "8"),
        ("Table 4.1", "Software and Hardware Environment Specifications", "11"),
        ("Table 4.2", "Functional Test Cases and Verification Results", "12"),
        ("Table 4.3", "Extraction Performance Comparison across Different NLP Approaches", "12"),
        ("Table 4.4", "Confusion Matrix for 1,000 Annotated Skill Verification Tokens", "13"),
        ("Table 5.1", "Comparative Analysis of Resume Screening and Analysis Approaches", "16")
    ]
    t_tbls_data = [[Paragraph(f"<b>{clean_text_for_xml(num)}</b>", ParagraphStyle('P1', parent=body_style, fontSize=7.5, leading=9.5)),
                    Paragraph(clean_text_for_xml(desc), ParagraphStyle('P2', parent=body_style, fontSize=7.5, leading=9.5)),
                    Paragraph(pg, ParagraphStyle('P3', parent=body_style, fontSize=7.5, leading=9.5, alignment=2))] for num, desc, pg in tables_list]
    t_tbls = Table(t_tbls_data, colWidths=[65, 360, 62])
    t_tbls.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 1.2), ('BOTTOMPADDING', (0,0), (-1,-1), 1.2)]))
    story.append(t_tbls)
    story.append(Spacer(1, 4))

    story.append(Paragraph("LIST OF FIGURES", h2_style))
    figures_list = [
        ("Figure 2.1", "Use case diagram for Resume Analysis System", "5"),
        ("Figure 2.2", "Sequence diagram of end-to-end resume check", "6"),
        ("Figure 3.1", "System architecture diagram (Five-Layer Architecture)", "7"),
        ("Figure 3.2", "Resume and job processing pipeline", "8"),
        ("Figure 3.3", "Module / class diagram", "9"),
        ("Figure 3.4", "Level-0 data flow diagram (Context Diagram)", "9"),
        ("Figure 3.5", "Level-1 data flow diagram", "9"),
        ("Figure 3.6", "Activity diagram - operational decision flow", "10"),
        ("Figure 4.1", "Skill taxonomy distribution across technical categories", "11"),
        ("Figure 4.2", "Home screen and upload interface of web application", "12"),
        ("Figure 4.3", "Result screen for a matched candidate profile", "12"),
        ("Figure 4.4", "Detected skill gaps and personalized upskilling roadmap", "12"),
        ("Figure 4.5", "Comparison of extraction methods on benchmark resumes", "13"),
        ("Figure 4.6", "Category-wise skill alignment & gap radar chart", "13"),
        ("Figure 4.7", "Confusion matrix of skill token detection", "14"),
        ("Figure 4.8", "Top 10 most frequently identified skills in benchmark resumes", "14")
    ]
    t_figs_data = [[Paragraph(f"<b>{clean_text_for_xml(num)}</b>", ParagraphStyle('P1', parent=body_style, fontSize=7.5, leading=9.5)),
                    Paragraph(clean_text_for_xml(desc), ParagraphStyle('P2', parent=body_style, fontSize=7.5, leading=9.5)),
                    Paragraph(pg, ParagraphStyle('P3', parent=body_style, fontSize=7.5, leading=9.5, alignment=2))] for num, desc, pg in figures_list]
    t_figs = Table(t_figs_data, colWidths=[65, 360, 62])
    t_figs.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 1.2), ('BOTTOMPADDING', (0,0), (-1,-1), 1.2)]))
    story.append(t_figs)
    story.append(Spacer(1, 4))

    story.append(Paragraph("LIST OF ABBREVIATIONS", h2_style))
    abbr_rows = []
    for i in range(0, len(ABBREVIATIONS), 2):
        item1 = ABBREVIATIONS[i]
        item2 = ABBREVIATIONS[i+1] if i+1 < len(ABBREVIATIONS) else ("", "")
        abbr_rows.append([
            Paragraph(f"<b>{item1[0]}</b>", ParagraphStyle('AB1', parent=body_style, fontSize=7, leading=8.5)),
            Paragraph(item1[1], ParagraphStyle('AB2', parent=body_style, fontSize=7, leading=8.5)),
            Paragraph(f"<b>{item2[0]}</b>", ParagraphStyle('AB3', parent=body_style, fontSize=7, leading=8.5)),
            Paragraph(item2[1], ParagraphStyle('AB4', parent=body_style, fontSize=7, leading=8.5))
        ])
    t_abbr = Table(abbr_rows, colWidths=[55, 185, 55, 192])
    t_abbr.setStyle(TableStyle([('TOPPADDING', (0,0), (-1,-1), 1), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    story.append(t_abbr)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION (Page 1)
    # -------------------------------------------------------------
    story.append(Paragraph("CHAPTER 1<br/>INTRODUCTION", h1_style))
    for block in CH1_INTRO.split('\n\n'):
        if block.startswith("1.1 ") or block.startswith("1.2 ") or block.startswith("1.3 "):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h2_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•'):
                    story.append(add_p(p_sub.strip()[1:].strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        elif block.startswith("1.1.1") or block.startswith("1.1.2") or block.startswith("1.1.3"):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h3_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    story.append(add_p(p_sub.strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        else:
            story.append(add_p(block.strip()))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # CHAPTER 2: SOFTWARE REQUIREMENT SPECIFICATION (Page 3)
    # -------------------------------------------------------------
    story.append(Paragraph("CHAPTER 2<br/>SOFTWARE REQUIREMENT SPECIFICATION", h1_style))
    for block in CH2_SRS.split('\n\n'):
        if any(block.startswith(f"2.{i} ") for i in range(1, 8)):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h2_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    story.append(add_p(p_sub.strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        elif any(block.startswith(f"2.1.{i}") for i in range(1, 9)):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h3_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•'):
                    story.append(add_p(p_sub.strip()[1:].strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        else:
            story.append(add_p(block.strip()))

    story.append(Image('bca_report_assets/fig_2_1_use_case.png', width=5.5*inch, height=3.5*inch))
    story.append(Paragraph("Figure 2.1: Use case diagram for Resume Analysis System", caption_style))
    story.append(Spacer(1, 4))

    # Table 2.1
    t21 = TABLES_DATA["2.1"]
    story.append(add_p(t21['title'], bold_prefix="Use Case Table: "))
    story.append(make_table(t21['headers'], t21['rows'], [130, 357]))
    story.append(Spacer(1, 8))

    story.append(Image('bca_report_assets/fig_2_2_sequence.png', width=5.5*inch, height=3.5*inch))
    story.append(Paragraph("Figure 2.2: Sequence diagram of one complete resume analysis check", caption_style))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # CHAPTER 3: SYSTEM DESIGN (Page 7)
    # -------------------------------------------------------------
    story.append(Paragraph("CHAPTER 3<br/>SYSTEM DESIGN", h1_style))
    for block in CH3_DESIGN.split('\n\n'):
        if any(block.startswith(f"3.{i} ") for i in range(1, 9)):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h2_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    story.append(add_p(p_sub.strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        else:
            story.append(add_p(block.strip()))

    story.append(Image('bca_report_assets/fig_3_1_architecture.png', width=5.5*inch, height=4.1*inch))
    story.append(Paragraph("Figure 3.1: System architecture diagram (Five-Layer Architecture)", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_3_2_pipeline.png', width=5.6*inch, height=2.1*inch))
    story.append(Paragraph("Figure 3.2: Resume and job processing pipeline", caption_style))
    story.append(Spacer(1, 4))

    # Table 3.1
    t31 = TABLES_DATA["3.1"]
    story.append(add_p(t31['title'], bold_prefix="Taxonomy Overview: "))
    story.append(make_table(t31['headers'], t31['rows'], [110, 50, 165, 162]))
    story.append(Spacer(1, 6))

    # Table 3.2
    t32 = TABLES_DATA["3.2"]
    story.append(add_p(t32['title'], bold_prefix="Feature Design: "))
    story.append(make_table(t32['headers'], t32['rows'], [115, 60, 160, 152]))
    story.append(Spacer(1, 6))

    story.append(Image('bca_report_assets/fig_3_3_class_diagram.png', width=5.5*inch, height=3.8*inch))
    story.append(Paragraph("Figure 3.3: Module / class diagram", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_3_4_dfd_level_0.png', width=5.4*inch, height=2.7*inch))
    story.append(Paragraph("Figure 3.4: Level-0 data flow diagram (Context Diagram)", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_3_5_dfd_level_1.png', width=5.5*inch, height=3.5*inch))
    story.append(Paragraph("Figure 3.5: Level-1 data flow diagram", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_3_6_activity.png', width=5.0*inch, height=4.4*inch))
    story.append(Paragraph("Figure 3.6: Activity diagram - operational decision flow", caption_style))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # CHAPTER 4: IMPLEMENTATION AND RESULTS (Page 11)
    # -------------------------------------------------------------
    story.append(Paragraph("CHAPTER 4<br/>IMPLEMENTATION AND RESULTS", h1_style))
    for block in CH4_IMPL_RESULTS.split('\n\n'):
        if any(block.startswith(f"4.{i} ") for i in range(1, 7)):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h2_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    story.append(add_p(p_sub.strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        elif any(block.startswith(f"4.4.{i}") for i in range(1, 3)):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h3_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•'):
                    story.append(add_p(p_sub.strip()[1:].strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        else:
            story.append(add_p(block.strip()))

    # Table 4.1
    t41 = TABLES_DATA["4.1"]
    story.append(add_p(t41['title'], bold_prefix="Environment Setup: "))
    story.append(make_table(t41['headers'], t41['rows'], [130, 180, 177]))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_1_taxonomy_dist.png', width=5.2*inch, height=2.9*inch))
    story.append(Paragraph("Figure 4.1: Skill taxonomy distribution across technical categories", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_2_ui_home.png', width=5.4*inch, height=3.2*inch))
    story.append(Paragraph("Figure 4.2: Home screen and upload interface of web application", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_3_ui_results.png', width=5.4*inch, height=3.3*inch))
    story.append(Paragraph("Figure 4.3: Result screen for a candidate matching a Python Developer role", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_4_ui_gaps.png', width=5.4*inch, height=3.3*inch))
    story.append(Paragraph("Figure 4.4: Detected skill gaps and personalized upskilling roadmap", caption_style))
    story.append(Spacer(1, 4))

    # Table 4.2
    t42 = TABLES_DATA["4.2"]
    story.append(add_p(t42['title'], bold_prefix="Functional Verification: "))
    story.append(make_table(t42['headers'], t42['rows'], [45, 140, 142, 115, 45]))
    story.append(Spacer(1, 4))

    # Table 4.3
    t43 = TABLES_DATA["4.3"]
    story.append(add_p(t43['title'], bold_prefix="Extraction Performance: "))
    story.append(make_table(t43['headers'], t43['rows'], [190, 75, 70, 72, 80]))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_5_method_comparison.png', width=5.3*inch, height=3.0*inch))
    story.append(Paragraph("Figure 4.5: Comparison of extraction methods on benchmark resumes", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_6_radar_chart.png', width=4.0*inch, height=4.0*inch))
    story.append(Paragraph("Figure 4.6: Category-wise skill alignment & gap radar chart", caption_style))
    story.append(Spacer(1, 4))

    # Table 4.4
    t44 = TABLES_DATA["4.4"]
    story.append(add_p(t44['title'], bold_prefix="Confusion Matrix: "))
    story.append(make_table(t44['headers'], t44['rows'], [170, 110, 110, 97]))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_7_confusion_matrix.png', width=4.2*inch, height=3.2*inch))
    story.append(Paragraph("Figure 4.7: Confusion matrix of skill token detection", caption_style))
    story.append(Spacer(1, 4))

    story.append(Image('bca_report_assets/fig_4_8_top_skills.png', width=5.2*inch, height=2.9*inch))
    story.append(Paragraph("Figure 4.8: Top 10 most frequently identified skills in benchmark resumes", caption_style))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # CHAPTER 5: CONCLUSION (Page 16)
    # -------------------------------------------------------------
    story.append(Paragraph("CHAPTER 5<br/>CONCLUSION", h1_style))
    for block in CH5_CONCLUSION.split('\n\n'):
        if any(block.startswith(f"5.{i} ") for i in range(1, 4)):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h2_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    story.append(add_p(p_sub.strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        else:
            story.append(add_p(block.strip()))

    # Table 5.1
    t51 = TABLES_DATA["5.1"]
    story.append(add_p(t51['title'], bold_prefix="Comparative Synthesis: "))
    story.append(make_table(t51['headers'], t51['rows'], [100, 95, 95, 95, 102]))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # APPENDIX A: SOURCE CODE (Page 17)
    # -------------------------------------------------------------
    story.append(Paragraph("APPENDIX A<br/>IMPORTANT SOURCE CODE", h1_style))
    story.append(add_p("The complete source code is modularly structured across dedicated Python files. Core operational modules are reproduced below:"))

    def add_pdf_code_block(title, code):
        story.append(Paragraph(f"<b>{clean_text_for_xml(title)}</b>", h3_style))
        # Wrap preformatted code
        escaped_code = clean_text_for_xml(code.strip())
        story.append(Preformatted(escaped_code, code_style))
        story.append(Spacer(1, 6))

    add_pdf_code_block("A.1 Flask Application Controller (app.py)", CODE_APP_PY)
    add_pdf_code_block("A.2 Document Text Stream Parser (resume_parser.py)", CODE_RESUME_PARSER)
    add_pdf_code_block("A.3 Text Preprocessor & Sanitizer (text_preprocessor.py)", CODE_TEXT_PREPROCESSOR)
    add_pdf_code_block("A.4 Skill Extractor & Taxonomy Matcher (skill_extractor.py)", CODE_SKILL_EXTRACTOR)
    add_pdf_code_block("A.5 Job Description Analyzer (job_analyzer.py)", CODE_JOB_ANALYZER)
    add_pdf_code_block("A.6 Skill Matcher & Scoring Engine (skill_matcher.py)", CODE_SKILL_MATCHER)
    add_pdf_code_block("A.7 Gap Detector & Upskilling Roadmap (gap_detector.py)", CODE_GAP_DETECTOR)
    add_pdf_code_block("A.8 Python Dependency Specification (requirements.txt)", CODE_REQUIREMENTS_TXT)
    add_pdf_code_block("A.9 Curated Skills Taxonomy Snippet (skills_taxonomy.json)", SAMPLE_TAXONOMY_JSON)
    add_pdf_code_block("A.10 Sample Test Job Description (sample_job_description.txt)", SAMPLE_JOB_DESCRIPTION)
    add_pdf_code_block("A.11 Sample Synthetic Candidate Resume (sample_resume.txt)", SAMPLE_SYNTHETIC_RESUME)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # APPENDIX B: HOW TO RUN THE PROJECT (Page 22)
    # -------------------------------------------------------------
    story.append(Paragraph("APPENDIX B<br/>HOW TO RUN THE PROJECT", h1_style))
    for block in APP_B_TEXT.split('\n\n'):
        if block.startswith("B.1 ") or block.startswith("B.2 ") or block.startswith("B.3 "):
            story.append(Paragraph(clean_text_for_xml(block.split('\n')[0]), h2_style))
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('```'):
                    continue
                elif p_sub.strip().startswith('•'):
                    story.append(add_p(p_sub.strip()[1:].strip(), is_bullet=True))
                elif p_sub.strip():
                    story.append(add_p(p_sub.strip()))
        else:
            story.append(add_p(block.strip()))
    story.append(PageBreak())

    # -------------------------------------------------------------
    # REFERENCES (Page 23)
    # -------------------------------------------------------------
    story.append(Paragraph("REFERENCES", h1_style))
    for ref in REFERENCES_DATA:
        story.append(Paragraph(clean_text_for_xml(ref), ParagraphStyle('Ref', parent=body_style, fontSize=8.5, leading=11, leftIndent=20, firstLineIndent=-20, spaceAfter=4)))

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF generation completed successfully!")

if __name__ == '__main__':
    build_pdf_document()
