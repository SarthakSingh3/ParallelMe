"""
build_docx_report.py
Generates the complete, professional, beautifully formatted DOCX project report.
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from docx_helpers import (
    add_styled_heading, add_body_p, add_bullet_p,
    add_image_figure, format_custom_table, set_table_borders,
    set_cell_background, set_cell_margins, sanitize_xml_text
)
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

def create_code_block(doc, code_str, title=""):
    code_str = sanitize_xml_text(code_str)
    if title:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(8)
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(sanitize_xml_text(title))
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(10.5)
        r_t.bold = True
        r_t.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.2)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(code_str.strip())
    r.font.name = 'Consolas'
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(6)

def generate_full_docx():
    print("Generating complete BCA Project Report in DOCX format...")
    doc = Document()
    
    # Configure A4 page margins (1 inch all around)
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

    # -------------------------------------------------------------
    # 1. COVER PAGE
    # -------------------------------------------------------------
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(20)
    p_top.paragraph_format.space_after = Pt(6)
    r = p_top.add_run("A Project Report\nOn")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(24)
    r_title = p_title.add_run(METADATA['title'])
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(10)
    p_sub.paragraph_format.space_after = Pt(4)
    r_sub = p_sub.add_run("Submitted in partial fulfillment of the\nrequirement for the award of the degree of")
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(10)
    p_deg.paragraph_format.space_after = Pt(2)
    r_deg = p_deg.add_run(f"{METADATA['degree']}\nDEGREE\n{METADATA['session']}\n{METADATA['stream']}")
    r_deg.font.name = 'Times New Roman'
    r_deg.font.size = Pt(12)
    r_deg.font.bold = True
    r_deg.font.color.rgb = RGBColor(0x11, 0x18, 0x27)

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_before = Pt(20)
    p_by.paragraph_format.space_after = Pt(4)
    r_by = p_by.add_run(f"By\n{METADATA['student_name']} (Admission No. {METADATA['roll_no']})")
    r_by.font.name = 'Times New Roman'
    r_by.font.size = Pt(12)
    r_by.font.bold = True

    p_gd = doc.add_paragraph()
    p_gd.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_gd.paragraph_format.space_before = Pt(18)
    p_gd.paragraph_format.space_after = Pt(4)
    r_gd = p_gd.add_run(f"Under the guidance of\n{METADATA['guide_name']}\n{METADATA['guide_desig']}")
    r_gd.font.name = 'Times New Roman'
    r_gd.font.size = Pt(11.5)
    r_gd.font.bold = True

    p_bot = doc.add_paragraph()
    p_bot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bot.paragraph_format.space_before = Pt(36)
    p_bot.paragraph_format.space_after = Pt(0)
    r_bot = p_bot.add_run(f"{METADATA['dept_name']}\n{METADATA['university_name']}, {METADATA['city']}\n{METADATA['country']}\n\n{METADATA['submission_date']}")
    r_bot.font.name = 'Times New Roman'
    r_bot.font.size = Pt(11)
    r_bot.font.bold = True
    r_bot.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 2. DECLARATION & CERTIFICATE
    # -------------------------------------------------------------
    p_dec_hdr = doc.add_paragraph()
    p_dec_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dec_hdr.paragraph_format.space_before = Pt(10)
    p_dec_hdr.paragraph_format.space_after = Pt(2)
    r = p_dec_hdr.add_run(f"{METADATA['dept_name']}\n{METADATA['university_name']}, {METADATA['city']}")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True

    add_styled_heading(doc, "CANDIDATE'S DECLARATION", level=1)
    for para in DECLARATION_TEXT.split('\n\n'):
        add_body_p(doc, para)

    p_sign1 = doc.add_paragraph()
    p_sign1.paragraph_format.space_before = Pt(8)
    p_sign1.paragraph_format.space_after = Pt(4)
    r = p_sign1.add_run(f"Student Name (Admission No.):\n{METADATA['student_name']} ({METADATA['roll_no']})")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10.5)
    r.bold = True

    p_sup = doc.add_paragraph()
    p_sup.paragraph_format.space_before = Pt(6)
    p_sup.paragraph_format.space_after = Pt(4)
    r = p_sup.add_run(SUPERVISOR_CONFIRMATION)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.italic = True

    p_guide_sign = doc.add_paragraph()
    p_guide_sign.paragraph_format.space_before = Pt(4)
    p_guide_sign.paragraph_format.space_after = Pt(12)
    r = p_guide_sign.add_run(f"Guide Name: {METADATA['guide_name']}\nDesignation: {METADATA['guide_desig']}\nSignature: ______________________     Date: ______________")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.bold = True

    # Certificate
    add_styled_heading(doc, "CERTIFICATE", level=1)
    add_body_p(doc, CERTIFICATE_TEXT)

    p_cert_sign = doc.add_paragraph()
    p_cert_sign.paragraph_format.space_before = Pt(20)
    p_cert_sign.paragraph_format.space_after = Pt(0)
    r = p_cert_sign.add_run(
        "Signature of Examiner(s)                                                Signature of Supervisor(s)\n"
        f"                                                                                        ({METADATA['guide_name']})\n"
        f"Date: {METADATA['submission_date']}\n"
        f"Place: {METADATA['city']}"
    )
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # 3. ACKNOWLEDGEMENTS & ABSTRACT
    # -------------------------------------------------------------
    add_styled_heading(doc, "ACKNOWLEDGEMENTS", level=1)
    for para in ACKNOWLEDGEMENTS_TEXT.split('\n\n'):
        add_body_p(doc, para)

    p_ack_sign = doc.add_paragraph()
    p_ack_sign.paragraph_format.space_before = Pt(8)
    p_ack_sign.paragraph_format.space_after = Pt(16)
    r = p_ack_sign.add_run(f"{METADATA['student_name']}\nAdmission No: {METADATA['roll_no']}")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10.5)
    r.bold = True

    add_styled_heading(doc, "ABSTRACT", level=1)
    add_body_p(doc, ABSTRACT_TEXT)

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(8)
    p_kw.paragraph_format.space_after = Pt(12)
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.font.name = 'Times New Roman'
    r_kwh.font.size = Pt(10.5)
    r_kwh.bold = True
    r_kwv = p_kw.add_run(", ".join(KEYWORDS) + ".")
    r_kwv.font.name = 'Times New Roman'
    r_kwv.font.size = Pt(10.5)
    r_kwv.italic = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # 4. TABLE OF CONTENTS
    # -------------------------------------------------------------
    add_styled_heading(doc, "TABLE OF CONTENTS", level=1)
    
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

    toc_tbl = doc.add_table(rows=len(toc_data) + 1, cols=2)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_tbl)
    
    # Headers
    toc_tbl.rows[0].cells[0].text = "Section Title"
    toc_tbl.rows[0].cells[1].text = "Page"
    set_cell_background(toc_tbl.rows[0].cells[0], "1B365D")
    set_cell_background(toc_tbl.rows[0].cells[1], "1B365D")
    for c in toc_tbl.rows[0].cells:
        for r in c.paragraphs[0].runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    for idx, (title, pg) in enumerate(toc_data):
        row = toc_tbl.rows[idx + 1]
        row.cells[0].text = title
        row.cells[1].text = pg
        bg_col = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        set_cell_background(row.cells[0], bg_col)
        set_cell_background(row.cells[1], bg_col)
        set_cell_margins(row.cells[0], top=40, bottom=40, left=100, right=100)
        set_cell_margins(row.cells[1], top=40, bottom=40, left=100, right=100)
        p0 = row.cells[0].paragraphs[0]
        p1 = row.cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for r in p0.runs + p1.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            if "CHAPTER" in title or "APPENDIX" in title or title in ["DECLARATION", "CERTIFICATE", "ACKNOWLEDGEMENTS", "ABSTRACT", "REFERENCES"]:
                r.font.bold = True

    for row in toc_tbl.rows:
        row.cells[0].width = Inches(5.2)
        row.cells[1].width = Inches(1.0)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 5. LIST OF TABLES, LIST OF FIGURES, LIST OF ABBREVIATIONS
    # -------------------------------------------------------------
    add_styled_heading(doc, "LIST OF TABLES", level=1)
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
    for num, desc, pg in tables_list:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"{num}   {desc} {' ' * (80 - len(desc))} {pg}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)

    add_styled_heading(doc, "LIST OF FIGURES", level=1)
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
    for num, desc, pg in figures_list:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"{num}   {desc} {' ' * (80 - len(desc))} {pg}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)

    add_styled_heading(doc, "LIST OF ABBREVIATIONS", level=1)
    abbr_tbl = doc.add_table(rows=len(ABBREVIATIONS) + 1, cols=2)
    abbr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(abbr_tbl)
    
    abbr_tbl.rows[0].cells[0].text = "Abbreviation"
    abbr_tbl.rows[0].cells[1].text = "Full Form / Definition"
    set_cell_background(abbr_tbl.rows[0].cells[0], "1B365D")
    set_cell_background(abbr_tbl.rows[0].cells[1], "1B365D")
    for c in abbr_tbl.rows[0].cells:
        for r in c.paragraphs[0].runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for idx, (ab, full) in enumerate(ABBREVIATIONS):
        row = abbr_tbl.rows[idx + 1]
        row.cells[0].text = ab
        row.cells[1].text = full
        bg_col = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        set_cell_background(row.cells[0], bg_col)
        set_cell_background(row.cells[1], bg_col)
        set_cell_margins(row.cells[0], top=30, bottom=30, left=100, right=100)
        set_cell_margins(row.cells[1], top=30, bottom=30, left=100, right=100)
        p0 = row.cells[0].paragraphs[0]
        p1 = row.cells[1].paragraphs[0]
        for r in p0.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)
            r.font.bold = True
        for r in p1.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9)

    for row in abbr_tbl.rows:
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.4)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # -------------------------------------------------------------
    add_styled_heading(doc, "CHAPTER 1\nINTRODUCTION", level=1)
    for block in CH1_INTRO.split('\n\n'):
        if block.startswith("1.1 ") or block.startswith("1.2 ") or block.startswith("1.3 "):
            add_styled_heading(doc, block.split('\n')[0], level=2)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•'):
                    add_bullet_p(doc, p_sub.strip()[1:].strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        elif block.startswith("1.1.1") or block.startswith("1.1.2") or block.startswith("1.1.3"):
            add_styled_heading(doc, block.split('\n')[0], level=3)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    add_bullet_p(doc, p_sub.strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        else:
            add_body_p(doc, block.strip())

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 2: SOFTWARE REQUIREMENT SPECIFICATION
    # -------------------------------------------------------------
    add_styled_heading(doc, "CHAPTER 2\nSOFTWARE REQUIREMENT SPECIFICATION", level=1)
    for block in CH2_SRS.split('\n\n'):
        if any(block.startswith(f"2.{i} ") for i in range(1, 8)):
            add_styled_heading(doc, block.split('\n')[0], level=2)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    add_bullet_p(doc, p_sub.strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        elif any(block.startswith(f"2.1.{i}") for i in range(1, 9)):
            add_styled_heading(doc, block.split('\n')[0], level=3)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•'):
                    add_bullet_p(doc, p_sub.strip()[1:].strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        else:
            add_body_p(doc, block.strip())

    # Figures & Tables for Ch 2
    add_image_figure(doc, 'bca_report_assets/fig_2_1_use_case.png', 'Figure 2.1: Use case diagram for Resume Analysis System')
    
    # Table 2.1
    t21 = TABLES_DATA["2.1"]
    add_body_p(doc, f"The detailed operational scenario for the primary use case is documented in {t21['title']}.", bold_prefix="Use Case Specification: ")
    tbl21 = doc.add_table(rows=len(t21['rows']) + 1, cols=2)
    format_custom_table(tbl21, [Inches(1.8), Inches(4.4)], t21['headers'], t21['rows'])
    
    add_image_figure(doc, 'bca_report_assets/fig_2_2_sequence.png', 'Figure 2.2: Sequence diagram of one complete resume analysis check')

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 3: SYSTEM DESIGN
    # -------------------------------------------------------------
    add_styled_heading(doc, "CHAPTER 3\nSYSTEM DESIGN", level=1)
    for block in CH3_DESIGN.split('\n\n'):
        if any(block.startswith(f"3.{i} ") for i in range(1, 9)):
            add_styled_heading(doc, block.split('\n')[0], level=2)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    add_bullet_p(doc, p_sub.strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        else:
            add_body_p(doc, block.strip())

    # Figures & Tables for Ch 3
    add_image_figure(doc, 'bca_report_assets/fig_3_1_architecture.png', 'Figure 3.1: System architecture diagram (Five-Layer Architecture)')
    add_image_figure(doc, 'bca_report_assets/fig_3_2_pipeline.png', 'Figure 3.2: Resume and job processing pipeline')
    
    # Table 3.1
    t31 = TABLES_DATA["3.1"]
    add_body_p(doc, f"The organization and distribution of indexed competencies within the curated taxonomy is summarized in {t31['title']}.", bold_prefix="Taxonomy Overview: ")
    tbl31 = doc.add_table(rows=len(t31['rows']) + 1, cols=4)
    format_custom_table(tbl31, [Inches(1.6), Inches(0.8), Inches(2.0), Inches(1.8)], t31['headers'], t31['rows'])

    # Table 3.2
    t32 = TABLES_DATA["3.2"]
    add_body_p(doc, f"The analytical features extracted from candidate resumes and job postings are defined in {t32['title']}.", bold_prefix="Feature Specification: ")
    tbl32 = doc.add_table(rows=len(t32['rows']) + 1, cols=4)
    format_custom_table(tbl32, [Inches(1.5), Inches(0.8), Inches(2.0), Inches(1.9)], t32['headers'], t32['rows'])

    add_image_figure(doc, 'bca_report_assets/fig_3_3_class_diagram.png', 'Figure 3.3: Module / class diagram')
    add_image_figure(doc, 'bca_report_assets/fig_3_4_dfd_level_0.png', 'Figure 3.4: Level-0 data flow diagram (Context Diagram)')
    add_image_figure(doc, 'bca_report_assets/fig_3_5_dfd_level_1.png', 'Figure 3.5: Level-1 data flow diagram')
    add_image_figure(doc, 'bca_report_assets/fig_3_6_activity.png', 'Figure 3.6: Activity diagram - operational decision flow')

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 4: IMPLEMENTATION AND RESULTS
    # -------------------------------------------------------------
    add_styled_heading(doc, "CHAPTER 4\nIMPLEMENTATION AND RESULTS", level=1)
    for block in CH4_IMPL_RESULTS.split('\n\n'):
        if any(block.startswith(f"4.{i} ") for i in range(1, 7)):
            add_styled_heading(doc, block.split('\n')[0], level=2)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    add_bullet_p(doc, p_sub.strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        elif any(block.startswith(f"4.4.{i}") for i in range(1, 3)):
            add_styled_heading(doc, block.split('\n')[0], level=3)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•'):
                    add_bullet_p(doc, p_sub.strip()[1:].strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        else:
            add_body_p(doc, block.strip())

    # Figures & Tables for Ch 4
    # Table 4.1
    t41 = TABLES_DATA["4.1"]
    add_body_p(doc, f"The experimental hardware and software environment is summarized in {t41['title']}.", bold_prefix="Environment Setup: ")
    tbl41 = doc.add_table(rows=len(t41['rows']) + 1, cols=3)
    format_custom_table(tbl41, [Inches(1.8), Inches(2.2), Inches(2.2)], t41['headers'], t41['rows'])

    add_image_figure(doc, 'bca_report_assets/fig_4_1_taxonomy_dist.png', 'Figure 4.1: Skill taxonomy distribution across technical categories')
    add_image_figure(doc, 'bca_report_assets/fig_4_2_ui_home.png', 'Figure 4.2: Home screen and upload interface of the web application')
    add_image_figure(doc, 'bca_report_assets/fig_4_3_ui_results.png', 'Figure 4.3: Result screen for a candidate matching a Python Developer role')
    add_image_figure(doc, 'bca_report_assets/fig_4_4_ui_gaps.png', 'Figure 4.4: Detected skill gaps and personalized upskilling roadmap')

    # Table 4.2
    t42 = TABLES_DATA["4.2"]
    add_body_p(doc, f"The system underwent rigorous functional verification across standard and edge-case scenarios as documented in {t42['title']}.", bold_prefix="Functional Verification: ")
    tbl42 = doc.add_table(rows=len(t42['rows']) + 1, cols=5)
    format_custom_table(tbl42, [Inches(0.8), Inches(1.8), Inches(1.7), Inches(1.3), Inches(0.6)], t42['headers'], t42['rows'])

    # Table 4.3
    t43 = TABLES_DATA["4.3"]
    add_body_p(doc, f"The statistical extraction performance of the proposed hybrid pipeline against baseline methods on 50 annotated synthetic resumes is reported in {t43['title']}.", bold_prefix="Extraction Metrics: ")
    tbl43 = doc.add_table(rows=len(t43['rows']) + 1, cols=5)
    format_custom_table(tbl43, [Inches(2.4), Inches(0.9), Inches(0.9), Inches(0.9), Inches(1.1)], t43['headers'], t43['rows'])

    add_image_figure(doc, 'bca_report_assets/fig_4_5_method_comparison.png', 'Figure 4.5: Comparison of extraction methods on benchmark resumes')
    add_image_figure(doc, 'bca_report_assets/fig_4_6_radar_chart.png', 'Figure 4.6: Category-wise skill alignment & gap radar chart')

    # Table 4.4
    t44 = TABLES_DATA["4.4"]
    add_body_p(doc, f"Detailed token-level classification performance is tabulated in {t44['title']}.", bold_prefix="Confusion Matrix: ")
    tbl44 = doc.add_table(rows=len(t44['rows']) + 1, cols=4)
    format_custom_table(tbl44, [Inches(2.2), Inches(1.4), Inches(1.4), Inches(1.2)], t44['headers'], t44['rows'])

    add_image_figure(doc, 'bca_report_assets/fig_4_7_confusion_matrix.png', 'Figure 4.7: Confusion matrix of skill token detection')
    add_image_figure(doc, 'bca_report_assets/fig_4_8_top_skills.png', 'Figure 4.8: Top 10 most frequently identified skills in benchmark resumes')

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 5: CONCLUSION
    # -------------------------------------------------------------
    add_styled_heading(doc, "CHAPTER 5\nCONCLUSION", level=1)
    for block in CH5_CONCLUSION.split('\n\n'):
        if any(block.startswith(f"5.{i} ") for i in range(1, 4)):
            add_styled_heading(doc, block.split('\n')[0], level=2)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('•') or (p_sub.strip() and p_sub.strip()[0].isdigit() and p_sub.strip()[1] in ['.', ' ']):
                    add_bullet_p(doc, p_sub.strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        else:
            add_body_p(doc, block.strip())

    # Table 5.1
    t51 = TABLES_DATA["5.1"]
    add_body_p(doc, f"A systematic comparison between existing screening methods and the proposed system is presented in {t51['title']}.", bold_prefix="Comparative Synthesis: ")
    tbl51 = doc.add_table(rows=len(t51['rows']) + 1, cols=5)
    format_custom_table(tbl51, [Inches(1.4), Inches(1.2), Inches(1.1), Inches(1.2), Inches(1.3)], t51['headers'], t51['rows'])

    doc.add_page_break()

    # -------------------------------------------------------------
    # APPENDIX A: SOURCE CODE
    # -------------------------------------------------------------
    add_styled_heading(doc, "APPENDIX A\nIMPORTANT SOURCE CODE", level=1)
    add_body_p(doc, "The complete source code is modularly structured across dedicated Python files. Core operational modules are reproduced below:")
    
    create_code_block(doc, CODE_APP_PY, "A.1 Flask Application Controller (app.py)")
    create_code_block(doc, CODE_RESUME_PARSER, "A.2 Document Text Stream Parser (resume_parser.py)")
    create_code_block(doc, CODE_TEXT_PREPROCESSOR, "A.3 Text Preprocessor & Sanitizer (text_preprocessor.py)")
    create_code_block(doc, CODE_SKILL_EXTRACTOR, "A.4 Skill Extractor & Taxonomy Matcher (skill_extractor.py)")
    create_code_block(doc, CODE_JOB_ANALYZER, "A.5 Job Description Analyzer (job_analyzer.py)")
    create_code_block(doc, CODE_SKILL_MATCHER, "A.6 Skill Matcher & Scoring Engine (skill_matcher.py)")
    create_code_block(doc, CODE_GAP_DETECTOR, "A.7 Gap Detector & Upskilling Roadmap (gap_detector.py)")
    create_code_block(doc, CODE_REQUIREMENTS_TXT, "A.8 Python Dependency Specification (requirements.txt)")
    create_code_block(doc, SAMPLE_TAXONOMY_JSON, "A.9 Curated Skills Taxonomy Snippet (skills_taxonomy.json)")
    create_code_block(doc, SAMPLE_JOB_DESCRIPTION, "A.10 Sample Test Job Description (sample_job_description.txt)")
    create_code_block(doc, SAMPLE_SYNTHETIC_RESUME, "A.11 Sample Synthetic Candidate Resume (sample_resume.txt)")

    doc.add_page_break()

    # -------------------------------------------------------------
    # APPENDIX B: HOW TO RUN THE PROJECT
    # -------------------------------------------------------------
    add_styled_heading(doc, "APPENDIX B\nHOW TO RUN THE PROJECT", level=1)
    for block in APP_B_TEXT.split('\n\n'):
        if block.startswith("B.1 ") or block.startswith("B.2 ") or block.startswith("B.3 "):
            add_styled_heading(doc, block.split('\n')[0], level=2)
            content = "\n".join(block.split('\n')[1:])
            for p_sub in content.split('\n'):
                if p_sub.strip().startswith('```'):
                    continue
                elif p_sub.strip().startswith('•'):
                    add_bullet_p(doc, p_sub.strip()[1:].strip())
                elif p_sub.strip():
                    add_body_p(doc, p_sub.strip())
        else:
            add_body_p(doc, block.strip())

    doc.add_page_break()

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    add_styled_heading(doc, "REFERENCES", level=1)
    for ref in REFERENCES_DATA:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        r = p.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)

    out_path = os.path.join("bca_report_output", "BCA_Project_Report_Resume_Analysis.docx")
    doc.save(out_path)
    print(f"Successfully generated DOCX report at: {out_path}")

if __name__ == '__main__':
    generate_full_docx()
