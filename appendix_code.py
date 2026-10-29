"""
appendix_code.py
Stores complete, syntactically valid source code for Appendix A and instructions for Appendix B.
"""

CODE_APP_PY = '''"""
app.py - Main Flask Application Controller
AI-Based Resume Analysis and Skill Gap Detection System
Run: python app.py -> http://127.0.0.1:5000
"""
import os
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

from resume_parser import parse_resume_document
from text_preprocessor import preprocess_resume_text
from skill_extractor import extract_skills_from_text
from job_analyzer import analyze_job_description
from skill_matcher import compute_skill_compatibility
from gap_detector import detect_skill_gaps, generate_upskilling_roadmap

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB Limit
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_resume_endpoint():
    # 1. Validate file presence
    if 'resume_file' not in request.files:
        return jsonify({'error': 'No resume file uploaded. Please select a .pdf or .docx file.'}), 400
    
    file = request.files['resume_file']
    job_text = request.form.get('job_description', '').strip()
    target_role = request.form.get('target_role', 'Custom Role').strip()

    if file.filename == '' or not is_allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Allowed formats are .pdf and .docx.'}), 400

    if not job_text:
        return jsonify({'error': 'Job description text cannot be empty.'}), 400

    # 2. Save temporary upload safely
    filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_path)

    try:
        # 3. Extract text from document
        raw_text = parse_resume_document(temp_path)
        if not raw_text or len(raw_text.strip()) < 20:
            return jsonify({'error': 'Unable to extract legible text from the uploaded document.'}), 400

        # 4. Preprocess and clean text
        cleaned_text, profile_meta = preprocess_resume_text(raw_text)

        # 5. Extract candidate skills using taxonomy
        candidate_skills = extract_skills_from_text(cleaned_text)

        # 6. Analyze job description requirements
        job_reqs = analyze_job_description(job_text)

        # 7. Compute compatibility and coverage
        match_result = compute_skill_compatibility(candidate_skills, job_reqs)

        # 8. Detect skill gaps and fetch recommendations
        gap_data = detect_skill_gaps(candidate_skills, job_reqs)
        roadmap = generate_upskilling_roadmap(gap_data['missing_required'])

        response_payload = {
            'filename': filename,
            'target_role': target_role,
            'candidate_profile': profile_meta,
            'candidate_skills_count': len(candidate_skills),
            'candidate_skills': candidate_skills,
            'job_required_skills': job_reqs['required_skills'],
            'job_preferred_skills': job_reqs['preferred_skills'],
            'match_metrics': match_result,
            'skill_gaps': gap_data,
            'upskilling_roadmap': roadmap
        }
        return jsonify(response_payload), 200

    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

    finally:
        # Purge temporary file to maintain user privacy
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/taxonomy', methods=['GET'])
def get_taxonomy():
    tax_path = os.path.join(os.path.dirname(__file__), 'skills_taxonomy.json')
    if os.path.exists(tax_path):
        with open(tax_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({'error': 'Taxonomy file not found.'}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
'''

CODE_RESUME_PARSER = '''"""
resume_parser.py - Text Stream Ingestion Module
Extracts plain text streams from PDF and DOCX document formats.
"""
import os
import fitz  # PyMuPDF
import docx

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text blocks from PDF preserving multi-column reading flow."""
    text_content = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            # get_text("blocks") returns sorted structural blocks: (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks")
            for b in blocks:
                if b[6] == 0:  # 0 indicates standard text block (not image)
                    text_content.append(b[4].strip())
    return "\\n".join(text_content)

def extract_text_from_docx(docx_path: str) -> str:
    """Extracts full text across paragraphs and embedded table cells."""
    doc = docx.Document(docx_path)
    text_parts = []
    # 1. Paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text.strip())
    # 2. Tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text_parts.append(cell.text.strip())
    return "\\n".join(text_parts)

def parse_resume_document(file_path: str) -> str:
    """Master router dispatching file extraction based on extension."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    ext = file_path.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: .{ext}")
'''

CODE_TEXT_PREPROCESSOR = '''"""
text_preprocessor.py - Text Sanitization and Profile Extraction
Cleans raw text, extracts contact metadata, and normalizes tokens.
"""
import re

EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
PHONE_REGEX = r'(?:\\+?\\d{1,3}[-.\\s]?)?\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}'
EDUCATION_KEYWORDS = [
    r'\\bBCA\\b', r'\\bMCA\\b', r'\\bB\\.Tech\\b', r'\\bBTech\\b', r'\\bM\\.Tech\\b',
    r'\\bB\\.Sc\\b', r'\\bBSc\\b', r'\\bM\\.Sc\\b', r'\\bBachelor\\b', r'\\bMaster\\b'
]

def preprocess_resume_text(raw_text: str):
    """Sanitizes text and returns clean body along with candidate metadata."""
    # 1. Extract contact metadata
    emails = re.findall(EMAIL_REGEX, raw_text)
    phones = re.findall(PHONE_REGEX, raw_text)
    
    edu_found = []
    for pattern in EDUCATION_KEYWORDS:
        if re.search(pattern, raw_text, re.IGNORECASE):
            edu_found.append(pattern.replace(r'\\b', '').replace('\\', ''))
            
    # 2. Experience heuristics (looking for patterns like 'X+ years' or 'X years')
    exp_matches = re.findall(r'(\\d+(?:\\.\\d+)?)\\s*\\+?\\s*(?:years?|yrs?)\\s*(?:of)?\\s*(?:experience)?', raw_text, re.IGNORECASE)
    detected_exp = float(exp_matches[0]) if exp_matches else 0.0

    profile_metadata = {
        'email': emails[0] if emails else 'Not Detected',
        'phone': phones[0] if phones else 'Not Detected',
        'education': list(set(edu_found)),
        'estimated_experience_years': detected_exp
    }

    # 3. Clean body text: remove bullets, non-ascii noise, multiple spaces
    cleaned = raw_text
    cleaned = re.sub(EMAIL_REGEX, ' ', cleaned)
    cleaned = re.sub(PHONE_REGEX, ' ', cleaned)
    cleaned = re.sub(r'[^a-zA-Z0-9\\+\\#\\.\\-\\s]', ' ', cleaned)
    cleaned = re.sub(r'\\s+', ' ', cleaned).strip()

    return cleaned, profile_metadata
'''

CODE_SKILL_EXTRACTOR = '''"""
skill_extractor.py - Taxonomy-Guided Entity Matching
Identifies technical and soft skills using boundary-safe regex & aliases.
"""
import os
import json
import re

TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), 'skills_taxonomy.json')

def load_skills_taxonomy():
    if os.path.exists(TAXONOMY_PATH):
        with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

SKILLS_TAXONOMY = load_skills_taxonomy()

def extract_skills_from_text(text: str) -> dict:
    """Extracts verified skills grouped by technical categories."""
    extracted = {
        'all_skills': [],
        'by_category': {}
    }
    lowered_text = f" {text.lower()} "

    for category, skills_dict in SKILLS_TAXONOMY.items():
        extracted['by_category'][category] = []
        for canonical_name, aliases in skills_dict.items():
            matched = False
            # Check all aliases including canonical representation
            search_terms = [canonical_name] + aliases
            for term in search_terms:
                term_clean = term.lower()
                # Boundary safe check preventing substring collision (e.g. Java inside JavaScript)
                escaped = re.escape(term_clean)
                pattern = rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])'
                if re.search(pattern, lowered_text):
                    matched = True
                    break
            
            if matched:
                extracted['all_skills'].append(canonical_name)
                extracted['by_category'][category].append(canonical_name)

    # De-duplicate list
    extracted['all_skills'] = sorted(list(set(extracted['all_skills'])))
    return extracted
'''

CODE_JOB_ANALYZER = '''"""
job_analyzer.py - Job Description Requirement Decomposition
Separates mandatory prerequisites from preferred qualifications.
"""
import re
from skill_extractor import extract_skills_from_text

REQUIRED_HEADERS = [r'requirements?', r'required skills?', r'must have', r'qualifications?', r'what you need']
PREFERRED_HEADERS = [r'preferred', r'nice to have', r'plus', r'bonus', r'good to have', r'desired']

def analyze_job_description(job_text: str) -> dict:
    """Parses job posting and extracts categorized skill requirements."""
    # Split text into sections if headers exist
    lines = job_text.split('\\n')
    req_lines = []
    pref_lines = []
    current_mode = 'req'  # default section

    for line in lines:
        line_clean = line.strip().lower()
        if any(re.search(h, line_clean) for h in PREFERRED_HEADERS):
            current_mode = 'pref'
            continue
        elif any(re.search(h, line_clean) for h in REQUIRED_HEADERS):
            current_mode = 'req'
            continue
            
        if current_mode == 'req':
            req_lines.append(line)
        else:
            pref_lines.append(line)

    req_text = "\\n".join(req_lines) if req_lines else job_text
    pref_text = "\\n".join(pref_lines)

    req_skills = extract_skills_from_text(req_text)['all_skills']
    pref_skills = extract_skills_from_text(pref_text)['all_skills']

    # Ensure mutual exclusivity (required takes precedence)
    pref_skills = [s for s in pref_skills if s not in req_skills]

    return {
        'required_skills': req_skills,
        'preferred_skills': pref_skills,
        'total_requirements_count': len(req_skills) + len(pref_skills)
    }
'''

CODE_SKILL_MATCHER = '''"""
skill_matcher.py - Mathematical Compatibility and Coverage Engine
Computes explainable match scores using normalized linear coverage weights.
"""

def compute_skill_compatibility(candidate_skills_dict: dict, job_reqs_dict: dict) -> dict:
    """Computes exact set-theoretic intersections and transparent match indices."""
    cand_set = set(candidate_skills_dict['all_skills'])
    req_set = set(job_reqs_dict['required_skills'])
    pref_set = set(job_reqs_dict['preferred_skills'])

    matched_req = sorted(list(cand_set.intersection(req_set)))
    matched_pref = sorted(list(cand_set.intersection(pref_set)))

    cov_req = (len(matched_req) / len(req_set) * 100) if len(req_set) > 0 else 100.0
    cov_pref = (len(matched_pref) / len(pref_set) * 100) if len(pref_set) > 0 else 100.0

    # Weighted scoring formula: 80% mandatory coverage, 20% preferred coverage
    total_score = round(0.80 * cov_req + 0.20 * cov_pref, 1)

    if total_score >= 80.0:
        verdict = "Strong Candidate Fit"
        badge_level = "success"
    elif total_score >= 50.0:
        verdict = "Moderate Candidate Fit"
        badge_level = "warning"
    else:
        verdict = "Significant Skill Gap"
        badge_level = "danger"

    return {
        'overall_match_score': total_score,
        'verdict': verdict,
        'badge_level': badge_level,
        'required_skill_coverage_pct': round(cov_req, 1),
        'preferred_skill_coverage_pct': round(cov_pref, 1),
        'matched_required': matched_req,
        'matched_preferred': matched_pref,
        'matched_count': len(matched_req) + len(matched_pref)
    }
'''

CODE_GAP_DETECTOR = '''"""
gap_detector.py - Skill Gap Detection and Recommendation Mapping
Isolates missing competencies and maps them to curated learning pathways.
"""

RECOMMENDATION_CATALOG = {
    "Docker": {
        "course": "Docker & Kubernetes for Web Developers",
        "platform": "freeCodeCamp / Coursera",
        "duration": "6 hours",
        "action": "Containerize your Flask and database project and push Dockerfile to GitHub."
    },
    "React": {
        "course": "Modern React Front to Back 2026",
        "platform": "Scrimba / YouTube",
        "duration": "14 hours",
        "action": "Build a responsive frontend component consuming your backend REST APIs."
    },
    "PostgreSQL": {
        "course": "Relational Databases & SQL Mastery",
        "platform": "edX / Codecademy",
        "duration": "8 hours",
        "action": "Migrate your local SQLite schema to PostgreSQL and write complex JOIN queries."
    },
    "Git": {
        "course": "Git & GitHub Version Control Essentials",
        "platform": "GitHub Skills / freeCodeCamp",
        "duration": "4 hours",
        "action": "Initialize repository, create feature branches, and submit clean pull requests."
    },
    "RESTful APIs": {
        "course": "Building Scalable RESTful Services with Python",
        "platform": "Real Python",
        "duration": "5 hours",
        "action": "Design CRUD endpoints following standard HTTP verbs and status codes."
    }
}

def detect_skill_gaps(candidate_skills_dict: dict, job_reqs_dict: dict) -> dict:
    cand_set = set(candidate_skills_dict['all_skills'])
    req_set = set(job_reqs_dict['required_skills'])
    pref_set = set(job_reqs_dict['preferred_skills'])

    missing_req = sorted(list(req_set - cand_set))
    missing_pref = sorted(list(pref_set - cand_set))

    return {
        'missing_required': missing_req,
        'missing_preferred': missing_pref,
        'total_gaps_count': len(missing_req) + len(missing_pref)
    }

def generate_upskilling_roadmap(missing_skills: list) -> list:
    roadmap = []
    for skill in missing_skills:
        info = RECOMMENDATION_CATALOG.get(skill, {
            "course": f"Foundations of {skill}",
            "platform": "Coursera / YouTube Open Courseware",
            "duration": "8-10 hours",
            "action": f"Review documentation and implement a mini-demonstration project using {skill}."
        })
        roadmap.append({
            'skill': skill,
            'course_title': info['course'],
            'platform': info['platform'],
            'estimated_duration': info['duration'],
            'suggested_action': info['action']
        })
    return roadmap
'''

CODE_REQUIREMENTS_TXT = '''Flask==3.1.0
werkzeug==3.1.3
spacy==3.7.5
PyMuPDF==1.24.10
pdfplumber==0.11.4
python-docx==1.1.2
pandas==2.2.3
numpy==2.1.2
matplotlib==3.9.2
scikit-learn==1.5.2
'''

SAMPLE_TAXONOMY_JSON = '''{
  "Programming Languages": {
    "Python": ["py", "python3"],
    "Java": ["core java", "j2se"],
    "JavaScript": ["js", "es6", "vanilla js"],
    "C++": ["cpp"],
    "Go": ["golang"],
    "TypeScript": ["ts"]
  },
  "Web Frameworks": {
    "Flask": ["flask microframework"],
    "Django": ["django rest framework", "drf"],
    "React": ["reactjs", "react.js"],
    "Node.js": ["nodejs", "node"]
  },
  "Databases": {
    "PostgreSQL": ["postgres", "pgsql"],
    "MySQL": ["mysql database"],
    "MongoDB": ["mongo", "nosql mongo"],
    "SQLite": ["sqlite3"]
  },
  "Cloud & DevOps": {
    "Docker": ["docker container", "dockerization"],
    "Git": ["github", "version control", "git flow"],
    "AWS": ["amazon web services", "ec2", "s3"],
    "CI/CD": ["continuous integration", "github actions", "jenkins"]
  }
}'''

SAMPLE_JOB_DESCRIPTION = """Target Role: Junior Full Stack Python Developer
Company: Apex Cloud Solutions

Requirements (Must Have):
- Bachelor's degree in Computer Applications (BCA) or equivalent.
- Strong proficiency in Python, Flask, and building RESTful APIs.
- Experience with relational databases, specifically PostgreSQL or MySQL.
- Familiarity with version control using Git and GitHub.
- Basic understanding of containerization using Docker.

Preferred (Nice to Have):
- Experience with React.js or modern frontend development.
- Familiarity with Automated Testing (PyTest) and CI/CD pipelines.
- Good problem-solving and communication skills."""

SAMPLE_SYNTHETIC_RESUME = """John Doe
john.doe@example.com | +91 98765 43210 | Greater Noida, India
LinkedIn: linkedin.com/in/johndoe-bca | GitHub: github.com/johndoe

EDUCATION
Bachelor of Computer Applications (BCA) - Core
Galgotias University, Greater Noida (2024 - 2027) | Current CGPA: 8.6/10

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, C++, HTML5, CSS3
- Web Frameworks & APIs: Flask, RESTful APIs, Bootstrap 5
- Databases: PostgreSQL, SQLite, MySQL
- Tools & Version Control: Git, GitHub, VS Code, Postman
- Soft Skills: Problem Solving, Team Collaboration, Communication

ACADEMIC PROJECTS
1. E-Commerce Backend Service (Flask, PostgreSQL, Git)
- Architected RESTful endpoints for user authentication, product catalog, and order processing.
- Utilized PostgreSQL for relational storage and Git for branching and versioning.

2. Student Portfolio Web Application (HTML5, CSS3, JavaScript)
- Created responsive user interface with modern UI/UX design and JavaScript validation.

3. Task Tracker API (Python, SQLite)
- Developed lightweight microservice with complete CRUD operations."""

APP_B_TEXT = """APPENDIX B: HOW TO RUN THE PROJECT

B.1 Project Directory Structure
The application repository is organized in a clean, maintainable directory hierarchy:
```text
resume-analyzer/
│
├── app.py                     # Main Flask web controller and REST API routes
├── resume_parser.py           # Multi-format document stream extractor (PDF/DOCX)
├── text_preprocessor.py       # Regex cleaner, sanitizer, and contact extractor
├── skill_extractor.py         # Boundary-safe taxonomy matcher and synonym resolver
├── job_analyzer.py            # Job description requirement parser
├── skill_matcher.py           # Mathematical scoring and skill coverage calculator
├── gap_detector.py            # Gap detection and learning roadmap generator
├── skills_taxonomy.json       # Curated ontology of 750+ normalized skills & aliases
├── requirements.txt           # Python dependency specification
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom responsive styles and animations
│   └── js/
│       └── app.js            # Client-side AJAX submission and DOM updater
│
├── templates/
│   └── index.html             # Bootstrap 5 responsive web dashboard
│
├── temp_uploads/              # Ephemeral directory for processing uploads
│
└── tests/
    └── test_suite.py          # Automated unit test suite verifying all modules
```

B.2 Step-by-Step Execution Guide

Step 1: Environment Preparation
Ensure Python 3.10 or higher is installed on the host machine. Verify installation:
```bash
python --version
```

Step 2: Create and Activate Virtual Environment
Isolate dependencies by creating a local virtual environment:
```bash
# Windows (PowerShell / Command Prompt)
python -m venv venv
venv\\Scripts\\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Step 3: Install Required Dependencies
Install all required libraries from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

Step 4: Download spaCy Language Model
Download the lightweight English language model pipeline:
```bash
python -m spacy download en_core_web_sm
```

Step 5: Launch the Application
Run the Flask server:
```bash
python app.py
```
The terminal will display the active WSGI server banner:
```text
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

Step 6: Access the Web Dashboard
Open any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox) and navigate to:
```text
http://127.0.0.1:5000
```

Step 7: Analyze a Resume
1. Drag and drop a sample resume (.pdf or .docx) into the upload dropzone.
2. Select a target job preset (e.g., "Junior Full Stack Python Developer") or paste a custom job description into the text area.
3. Click the green "Analyze Resume & Detect Gaps" button.
4. The dashboard will compute results and render the compatibility gauge, matched skills badges, missing skill gaps, and the upskilling roadmap in under 0.5 seconds.

B.3 Troubleshooting Common Issues
• Issue: `ModuleNotFoundError: No module named 'fitz'`
  Resolution: Run `pip install PyMuPDF`. Ensure you do not install the legacy `fitz` package.
• Issue: `Error: No text extracted from document`
  Resolution: Confirm that the PDF contains live, selectable text rather than a flattened raster bitmap image scan.
• Issue: Port 5000 already in use
  Resolution: Change port in `app.py` from 5000 to 5050 (`app.run(port=5050)`)."""

print("appendix_code.py initialized successfully.")
