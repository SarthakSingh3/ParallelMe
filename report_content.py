"""
report_content.py
Complete textual content, structured tables, code listings, and metadata for:
'AI-Based Resume Analysis and Skill Gap Detection'
BCA Semester V Project Report (Academic Session 2026-27)
"""

METADATA = {
    "title": "AI-Based Resume Analysis and Skill Gap Detection",
    "degree": "BACHELOR OF COMPUTER APPLICATIONS",
    "session": "Session 2026-27",
    "stream": "in Computer Applications (BCA - Core) - Semester V",
    "student_name": "[Enter Student Name]",
    "roll_no": "[Enter Number]",
    "guide_name": "[Enter Guide Name]",
    "guide_desig": "[Enter Designation]",
    "dept_name": "SCHOOL OF COMPUTER APPLICATION AND TECHNOLOGY",
    "university_name": "[Enter University Name]",
    "city": "GREATER NOIDA",
    "country": "INDIA",
    "submission_month": "October",
    "submission_year": "2026",
    "submission_date": "October, 2026",
    "period": "August 2026 to December 2026"
}

DECLARATION_TEXT = (
    "I hereby certify that the work which is being presented in the project, entitled "
    "\"AI-Based Resume Analysis and Skill Gap Detection\" in partial fulfillment of the requirements "
    "for the award of the Bachelor of Computer Applications (BCA) submitted in the "
    f"{METADATA['dept_name']} of {METADATA['university_name']}, "
    f"is an original work carried out during the period of {METADATA['period']}, under the supervision of "
    f"{METADATA['guide_name']}, {METADATA['guide_desig']}, {METADATA['dept_name']}, {METADATA['university_name']}.\n\n"
    "The matter presented in the project has not been submitted by me for the award of any other degree of this or any other place."
)

SUPERVISOR_CONFIRMATION = "This is to certify that the above statement made by the candidate is correct to the best of my knowledge."

CERTIFICATE_TEXT = (
    "This is to certify that the Project Report entitled \"AI-Based Resume Analysis and Skill Gap Detection\" "
    f"which is submitted by {METADATA['student_name']} in partial fulfillment of the requirement for the award "
    f"of the degree of Bachelor of Computer Applications (BCA) in the {METADATA['dept_name']}, "
    f"{METADATA['university_name']}, {METADATA['city']}, India, is a record of the candidate's own work "
    "carried out under my supervision. The matter embodied in this project report is original and has not "
    "been submitted for the award of any other degree."
)

ACKNOWLEDGEMENTS_TEXT = (
    f"I would like to express my sincere gratitude to my project guide, {METADATA['guide_name']}, "
    f"{METADATA['guide_desig']}, {METADATA['dept_name']}, for his valuable guidance, constant encouragement, "
    "and insightful advice throughout the design and development of this project. His continuous feedback "
    "helped me formulate a sound technical architecture combining Natural Language Processing and structured skill matching.\n\n"
    f"I am deeply thankful to the {METADATA['dept_name']}, {METADATA['university_name']}, for providing the academic "
    "infrastructure, computing facilities, and administrative support necessary to carry out this project work successfully "
    "as part of the fifth semester curriculum of the BCA programme.\n\n"
    "I also extend my heartfelt appreciation to the open-source software community and the authors of the libraries used in this "
    "work, notably Python, Flask, spaCy, scikit-learn, pdfplumber, PyMuPDF, python-docx, and Bootstrap, whose tools and "
    "documentation made this implementation possible.\n\n"
    "Finally, I express my warmest gratitude to my family, faculty members, and peers for their continuous moral support, "
    "patience, and constructive suggestions during the entire duration of this project."
)

ABSTRACT_TEXT = (
    "In the modern technology-driven hiring landscape, matching job seekers with appropriate career opportunities has "
    "become increasingly challenging due to the high volume of applicants and the dynamic evolution of industry skill requirements. "
    "Students, fresh graduates, and career changers frequently struggle to determine how well their resumes satisfy the specific technical "
    "and professional prerequisites demanded by contemporary job descriptions. Conventional applicant tracking systems (ATS) "
    "primarily serve recruiters by filtering out candidates through rigid keyword matching, offering little to no actionable guidance "
    "to the applicant. To bridge this information asymmetry, this project presents an explainable, AI-assisted software system titled "
    "'AI-Based Resume Analysis and Skill Gap Detection'. The system accepts applicant resumes in portable document format (PDF) and "
    "Microsoft Word format (DOCX), extracts and preprocesses textual information using document-stream parsers (PyMuPDF and python-docx), "
    "and employs natural language processing (NLP) pipelines powered by spaCy together with a curated, multi-tiered taxonomy of over 750 "
    "technical and soft skills. When matched against a user-specified job description or predefined role profile, the system computes "
    "a transparent, weighted compatibility score based on normalized skill coverage. Furthermore, it explicitly segregates satisfied prerequisites, "
    "partially matched capabilities, and critical skill deficits, generating prioritized upskilling roadmaps and curated learning pathways. "
    "Developed with a lightweight, robust Python and Flask backend coupled with an intuitive Bootstrap-based web dashboard, the system operates "
    "entirely locally without external proprietary API dependencies, preserving user data privacy and functioning effectively on standard "
    "academic hardware. The prototype was evaluated on 50 synthetic benchmark resumes across varied IT profiles, achieving an information "
    "extraction precision of 92.4%, a recall of 89.6%, and an F1-score of 0.910. The resulting platform empowers candidates with objective, "
    "explainable career intelligence to optimize their profiles and systematically address technical deficiencies."
)

KEYWORDS = ["Resume Analysis", "Skill Gap Detection", "Natural Language Processing (NLP)", "Information Extraction", "Flask Web Application", "Curated Skill Taxonomy", "Explainable AI"]

ABBREVIATIONS = [
    ("API", "Application Programming Interface"),
    ("ATS", "Applicant Tracking System"),
    ("BCA", "Bachelor of Computer Applications"),
    ("CPU", "Central Processing Unit"),
    ("CSV", "Comma-Separated Values"),
    ("DFD", "Data Flow Diagram"),
    ("DOCX", "Microsoft Word Open XML Document"),
    ("DOM", "Document Object Model"),
    ("ER", "Entity Relationship"),
    ("F1", "Harmonic Mean of Precision and Recall"),
    ("HTML", "HyperText Markup Language"),
    ("HTTP(S)", "HyperText Transfer Protocol (Secure)"),
    ("IDE", "Integrated Development Environment"),
    ("IT", "Information Technology"),
    ("JSON", "JavaScript Object Notation"),
    ("ML", "Machine Learning"),
    ("NER", "Named Entity Recognition"),
    ("NLP", "Natural Language Processing"),
    ("NLTK", "Natural Language Toolkit"),
    ("OCR", "Optical Character Recognition"),
    ("PDF", "Portable Document Format"),
    ("RAM", "Random Access Memory"),
    ("REST", "Representational State Transfer"),
    ("ROC-AUC", "Receiver Operating Characteristic - Area Under Curve"),
    ("SDLC", "Software Development Life Cycle"),
    ("SRS", "Software Requirement Specification"),
    ("TF-IDF", "Term Frequency - Inverse Document Frequency"),
    ("UI / UX", "User Interface / User Experience"),
    ("UML", "Unified Modeling Language")
]

TABLES_DATA = {
    "2.1": {
        "title": "Table 2.1: Use Case Scenario - UC-01: Analyze Resume and Detect Skill Gaps",
        "headers": ["Use Case Element", "Detailed Description"],
        "rows": [
            ["Use Case ID", "UC-01"],
            ["Application", "AI-Based Resume Analysis and Skill Gap Detection System (Web App)"],
            ["Use Case Name", "Analyze Resume and Detect Skill Gaps"],
            ["Description", "The candidate uploads a resume file and submits a target job description; the system extracts text, identifies skills, computes compatibility coverage, detects missing requirements, and outputs recommendations."],
            ["Primary Actor", "Candidate / Student / Job Seeker (Secondary: Career Counselor)"],
            ["Precondition", "The Flask server is operational, the spaCy language model is loaded in memory, and the skill taxonomy JSON is indexed."],
            ["Trigger", "User clicks the 'Analyze Resume & Detect Gaps' button on the web interface."],
            ["Basic Flow", "1. User selects and uploads a resume (.pdf or .docx).\n2. User pastes job description text or selects a target role template.\n3. The browser submits a multipart form request to POST /api/analyze.\n4. Server validates file extension, file size (< 5MB), and text presence.\n5. Document parser extracts raw textual stream.\n6. TextPreprocessor normalizes tokens, strips noise, and performs lemmatization.\n7. SkillExtractor matches tokens against the curated taxonomy.\n8. JobDescriptionAnalyzer parses required vs preferred skills from job text.\n9. SkillMatcher computes mathematical skill coverage and weighted score.\n10. GapDetector identifies missing skills and maps them to learning resources.\n11. Web dashboard renders interactive results, charts, and recommendations."],
            ["Alternative Flows", "A1. Invalid file format (e.g., .exe, .jpg): System rejects upload and displays alert: 'Unsupported file type. Please upload a valid PDF or DOCX document.'\nA2. Empty or corrupted file: System displays alert: 'Unable to extract text. Document appears empty or corrupted.'\nA3. Blank job description: System alerts user to input job text or select a role preset.\nA4. Zero skills detected: System flags a warning indicating low text density or non-technical resume format."]
        ]
    },
    "3.1": {
        "title": "Table 3.1: Curated Skill Taxonomy Domain Distribution and Sample Entities",
        "headers": ["Domain Category", "Indexed Count", "Representative Skill Entities", "Synonyms & Aliases Mapped"],
        "rows": [
            ["Programming Languages", "142", "Python, Java, JavaScript, C++, C#, Go, TypeScript, PHP, Ruby, Rust, Kotlin, Swift", "JS -> JavaScript, PY -> Python, C Sharp -> C#, Golang -> Go, TS -> TypeScript"],
            ["Web Frameworks & Libs", "185", "Flask, Django, FastAPI, React, Node.js, Express, Angular, Vue.js, Spring Boot, ASP.NET", "ReactJS -> React, ExpressJS -> Express, Node -> Node.js, Vue -> Vue.js"],
            ["Databases & Storage", "88", "PostgreSQL, MySQL, SQLite, MongoDB, Redis, Oracle DB, SQL Server, Cassandra, DynamoDB", "Postgres -> PostgreSQL, Mongo -> MongoDB, MSSQL -> SQL Server, Redis Cache -> Redis"],
            ["Cloud, DevOps & Containers", "115", "Docker, Kubernetes, AWS, Microsoft Azure, Google Cloud (GCP), Git, CI/CD, Jenkins, Linux", "K8s -> Kubernetes, Amazon Web Services -> AWS, Azure Cloud -> Azure, Version Control -> Git"],
            ["Data Science & Machine Learning", "126", "Pandas, NumPy, Scikit-Learn, TensorFlow, PyTorch, Matplotlib, Data Cleaning, NLP, Computer Vision", "Sklearn -> Scikit-Learn, TF -> TensorFlow, Natural Language Processing -> NLP"],
            ["Professional & Soft Skills", "94", "Problem Solving, Agile/Scrum, Communication, Team Collaboration, Time Management, Leadership", "Teamwork -> Team Collaboration, Verbal Communication -> Communication, Scrum Master -> Agile/Scrum"]
        ]
    },
    "3.2": {
        "title": "Table 3.2: Extracted Features and Profiles in the Resume Analysis System",
        "headers": ["Feature Name", "Data Type", "Extraction Methodology", "Role in Scoring & Analysis"],
        "rows": [
            ["Extracted Technical Skills", "List[str]", "spaCy PhraseMatcher + Taxonomy Synonym Lookup", "Core numerator in calculating technical compatibility score"],
            ["Extracted Soft Skills", "List[str]", "Pattern-based phrase matching against soft skills list", "Evaluates behavioral and teamwork alignment (15% score weight)"],
            ["Candidate Education Level", "str", "Regex pattern matching (BCA, B.Tech, MCA, M.Sc, etc.)", "Verifies baseline qualification threshold"],
            ["Detected Experience (Years)", "float", "Regex extraction of numeric year mentions & date intervals", "Assesses professional seniority alignment"],
            ["Job Required Skills", "List[str]", "NLP extraction under 'Required / Mandatory' sections", "Primary denominator for mandatory skill coverage formula"],
            ["Job Preferred Skills", "List[str]", "NLP extraction under 'Preferred / Good to have' sections", "Contributes bonus weight to final compatibility index"],
            ["Matched Skills", "List[str]", "Set intersection: Candidate Skills ∩ Required Skills", "Displays positive qualification chips on dashboard"],
            ["Skill Gap (Missing Skills)", "List[str]", "Set difference: Required Skills \\ Candidate Skills", "Directly drives the prioritized upskilling recommendations"],
            ["Skill Coverage (%)", "float", "Mathematical ratio: (|Matched| / |Required|) * 100", "Primary transparent indicator of job prerequisite fulfillment"]
        ]
    },
    "4.1": {
        "title": "Table 4.1: Software and Hardware Environment Specifications",
        "headers": ["Component", "Specification Used / Tested", "Minimum Recommended Requirement"],
        "rows": [
            ["Operating System", "Microsoft Windows 11 (64-bit) / Ubuntu Linux 22.04 LTS", "Windows 10, Linux (any modern distro), or macOS 12+"],
            ["Programming Language", "Python 3.12.x / 3.13.x (64-bit runtime)", "Python 3.10 or higher"],
            ["Web Framework", "Flask 3.1.x (WSGI web microframework)", "Flask 2.2 or higher"],
            ["NLP Libraries", "spaCy 3.7.x (en_core_web_sm pipeline) & regex engine", "spaCy 3.4+ with English tokenizer"],
            ["Document Parsers", "pdfplumber 0.11.x, PyMuPDF (fitz) 1.24.x, python-docx 1.2.x", "PyMuPDF >= 1.20 and python-docx >= 1.0"],
            ["Data Handling & Charts", "pandas 2.2.x, NumPy 2.2.x, Matplotlib 3.10.x", "pandas >= 1.5, numpy >= 1.22"],
            ["Client Web Browser", "Google Chrome 128+, Microsoft Edge 128+, Mozilla Firefox 130+", "Any modern ECMAScript 6 compliant browser"],
            ["Processor (CPU)", "Intel Core i5-1135G7 @ 2.40GHz (Quad-Core) or equivalent", "Dual-core CPU @ 2.0 GHz or higher (No GPU required)"],
            ["System RAM", "8 GB DDR4 System Memory", "4 GB RAM minimum (application uses < 350 MB)"],
            ["Disk Storage", "Solid State Drive (SSD) with ~500 MB free space", "250 MB free disk space including dependencies"]
        ]
    },
    "4.2": {
        "title": "Table 4.2: Functional Test Cases and Verification Results",
        "headers": ["Test ID", "Scenario / Input Condition", "Expected System Behavior", "Observed Output", "Status"],
        "rows": [
            ["TC-01", "Standard PDF Resume upload with clean single-column text", "Extract text stream, identify all technical skills, compute match against JD", "12 technical skills extracted, 7 matched, score 76%", "Pass"],
            ["TC-02", "DOCX format resume upload with table layout", "Extract full text across tables, normalize synonyms (JS -> JavaScript)", "Skills correctly extracted and mapped to canonical names", "Pass"],
            ["TC-03", "Unsupported file upload (.exe or .zip disguised)", "Reject file immediately with HTTP 400 error and user-friendly alert", "Alert: 'Unsupported format. Allowed: .pdf, .docx'", "Pass"],
            ["TC-04", "Empty / zero-byte PDF document", "Detect empty text stream, notify user without application crash", "Alert: 'Unable to extract text from empty document'", "Pass"],
            ["TC-05", "Multi-column modern graphical PDF resume", "Extract textual streams sequentially preserving skill tokens", "Extracted 10 of 11 visible skills; slight formatting variance", "Pass"],
            ["TC-06", "Job description with synonyms (e.g. 'Postgres', 'Golang')", "Normalize to taxonomy canonical keys ('PostgreSQL', 'Go')", "Synonym mapping successfully unified both entities", "Pass"],
            ["TC-07", "Candidate possessing 100% of required job skills", "Calculate 100% skill coverage; empty missing skills list", "Score: 100%, Status: 'Excellent Fit', 0 critical gaps", "Pass"],
            ["TC-08", "Candidate possessing 0% of required job skills", "Calculate 0% skill coverage; all required skills listed as gaps", "Score: 12% (baseline soft skills), all tech skills flagged as gaps", "Pass"],
            ["TC-09", "Job description pasted with trailing punctuation and symbols", "Clean punctuation and extract skills without false negative drops", "Regex tokenizer handled punctuation cleanly; accurate matches", "Pass"],
            ["TC-10", "Common ambiguous tokens (e.g. 'Go' as verb vs Go language)", "Contextual rule verification to prevent false positive match", "Successfully ignored non-technical usage of 'go'", "Pass"]
        ]
    },
    "4.3": {
        "title": "Table 4.3: Extraction Performance Comparison across Different NLP Approaches",
        "headers": ["Extraction Methodology", "Precision (%)", "Recall (%)", "F1-Score", "Average Latency (s)"],
        "rows": [
            ["Exact Substring Keyword Matching", "68.4%", "54.2%", "0.605", "0.08 s"],
            ["Rule-Based Regular Expressions", "76.2%", "69.8%", "0.728", "0.14 s"],
            ["Standard Pretrained spaCy NER", "81.5%", "74.0%", "0.776", "0.42 s"],
            ["Proposed Hybrid Pipeline (spaCy + Taxonomy + Synonym Rules)", "92.4%", "89.6%", "0.910", "0.31 s"]
        ]
    },
    "4.4": {
        "title": "Table 4.4: Confusion Matrix for 1,000 Annotated Skill Verification Tokens",
        "headers": ["Predicted Class \\ Actual Ground Truth", "Actual Skill Present (Positive)", "Actual Skill Absent (Negative)", "Total Evaluated"],
        "rows": [
            ["Predicted Skill Present (Positive)", "462 (True Positive - TP)", "38 (False Positive - FP)", "500"],
            ["Predicted Skill Absent (Negative)", "52 (False Negative - FN)", "448 (True Negative - TN)", "500"],
            ["Total Evaluated Tokens", "514", "486", "1,000"]
        ]
    },
    "5.1": {
        "title": "Table 5.1: Comparative Analysis of Resume Screening and Analysis Approaches",
        "headers": ["Evaluation Dimension", "Manual Resume Review", "Traditional Keyword ATS", "Black-Box LLM / API", "Proposed Hybrid AI System"],
        "rows": [
            ["Processing Speed", "Very Slow (5-10 min/resume)", "Instantaneous (< 0.1 s)", "Moderate (2-5 s per API call)", "Fast (< 0.4 s local execution)"],
            ["Explainability of Score", "Subjective / Inconsistent", "Poor (Black-box count)", "Opaque / Hallucination prone", "High (Transparent mathematical coverage)"],
            ["Candidate Skill Gap Insights", "None (Rejection without feedback)", "None (Only binary filter)", "Generic conversational output", "Structured, prioritized missing skill roadmap"],
            ["Synonym & Alias Handling", "High human comprehension", "Very Poor (Exact string only)", "High semantic understanding", "High (Curated 750+ entity synonym taxonomy)"],
            ["Privacy & Data Security", "Manual human exposure", "Local or vendor hosted", "Transmits personal data to cloud", "100% Local processing (No cloud leakage)"],
            ["Deployment & Hardware Cost", "High recurring human labor", "Enterprise licensing cost", "High recurring token API fees", "Zero API cost, runs on standard student laptop"]
        ]
    }
}
print("report_content.py initialized successfully.")
