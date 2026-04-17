from flask import Flask, render_template_string, request
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "cv_builder_secret_key"

cv_data = {}
current_step = 0

def init_db():
    conn = sqlite3.connect("cv.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.commit()
    conn.close()

init_db()

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Professional CV Builder</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Segoe UI", sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); min-height: 100vh; padding: 2rem; }
.container { max-width: 900px; margin: 0 auto; }
header { text-align: center; color: white; margin-bottom: 2rem; }
header h1 { font-size: 2.2rem; font-weight: 300; letter-spacing: 2px; }
header span { color: #e94560; font-weight: 600; }
.progress { display: flex; justify-content: center; gap: 0.5rem; margin-bottom: 2rem; flex-wrap: wrap; }
.step { padding: 0.6rem 1rem; background: rgba(255,255,255,0.1); color: white; border-radius: 20px; font-size: 0.8rem; transition: all 0.3s; }
.step.active { background: #e94560; transform: scale(1.05); }
.form-box { background: white; border-radius: 15px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
.form-section { display: none; }
.form-section.active { display: block; animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.form-section h3 { color: #1a1a2e; margin-bottom: 1.5rem; border-bottom: 2px solid #e94560; padding-bottom: 0.5rem; font-size: 1.2rem; display: flex; align-items: center; gap: 10px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.4rem; font-weight: 600; color: #333; font-size: 0.9rem; }
.form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.7rem; border: 2px solid #ddd; border-radius: 8px; font-size: 0.95rem; transition: border-color 0.3s; }
.form-group input:focus, .form-group textarea:focus, .form-group select:focus { border-color: #e94560; outline: none; }
.form-group textarea { min-height: 90px; resize: vertical; }
.entry { background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #e94560; }
.photo-area { text-align: center; margin-bottom: 1.5rem; }
.photo-preview { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #e94560; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
.file-upload { display: inline-block; padding: 0.7rem 1.5rem; background: #0f3460; color: white; border-radius: 8px; cursor: pointer; font-weight: 600; }
.file-upload:hover { background: #16213e; }
.file-upload input { display: none; }
.btns { display: flex; justify-content: space-between; margin-top: 2rem; gap: 1rem; flex-wrap: wrap; }
.btn { padding: 0.9rem 1.8rem; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 0.95rem; transition: all 0.3s; }
.btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
.btn-primary { background: #e94560; color: white; }
.btn-secondary { background: #0f3460; color: white; }
.btn-success { background: #27ae60; color: white; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-add { background: #3498db; color: white; padding: 0.6rem 1.2rem; font-size: 0.85rem; }

/* CV Preview - Professional Sidebar Layout */
.preview { display: none; margin-top: 2rem; }
.preview.active { display: block; }
.cv-paper { background: white; max-width: 850px; margin: 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
.cv-container { display: flex; min-height: 1100px; }
.cv-sidebar { background: linear-gradient(180deg, #1a1a2e 0%, #0f3460 100%); color: white; width: 260px; padding: 30px 20px; flex-shrink: 0; }
.cv-main { flex: 1; padding: 35px; background: #fafafa; }
.cv-sidebar-photo { text-align: center; margin-bottom: 25px; }
.cv-sidebar-photo img { width: 130px; height: 130px; border-radius: 50%; border: 4px solid rgba(255,255,255,0.3); object-fit: cover; }
.cv-sidebar-name { font-size: 1.5rem; font-weight: 700; text-align: center; margin-bottom: 5px; letter-spacing: 1px; }
.cv-sidebar-title { font-size: 0.95rem; text-align: center; color: #e94560; margin-bottom: 25px; font-weight: 300; }
.cv-sidebar-section { margin-bottom: 25px; }
.cv-sidebar-section h4 { color: #e94560; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 6px; }
.cv-sidebar-contact { font-size: 0.8rem; line-height: 1.7; }
.cv-sidebar-contact span { display: block; }
.cv-sidebar-contact .label { color: #aaa; margin-right: 6px; }
.cv-sidebar-skills { display: flex; flex-wrap: wrap; gap: 6px; }
.cv-sidebar-skill { background: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 15px; font-size: 0.75rem; }
.cv-main-name { font-size: 2.2rem; color: #1a1a2e; font-weight: 700; margin-bottom: 3px; }
.cv-main-title { font-size: 1.1rem; color: #e94560; margin-bottom: 20px; font-weight: 300; }
.cv-section { margin-bottom: 25px; }
.cv-section h2 { color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 6px; margin-bottom: 15px; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; }
.cv-entry { margin-bottom: 15px; padding-left: 12px; border-left: 3px solid #e94560; }
.cv-entry-title { font-weight: bold; color: #333; font-size: 1rem; }
.cv-entry-sub { color: #666; font-style: italic; }
.cv-entry-date { color: #888; font-size: 0.85rem; margin-bottom: 6px; }
.cv-entry-desc { color: #555; line-height: 1.5; font-size: 0.9rem; }
.cv-skills-list { display: flex; flex-wrap: wrap; gap: 8px; }
.cv-skill-tag { background: white; border: 1px solid #ddd; padding: 6px 14px; border-radius: 20px; color: #333; font-size: 0.85rem; }
.cv-project { background: white; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #e94560; }
.cv-project-title { font-weight: bold; color: #1a1a2e; }
.cv-project-tech { color: #e94560; font-size: 0.8rem; margin: 4px 0; }
.cv-project-desc { color: #555; font-size: 0.9rem; }
.cv-cert-item, .cv-achievement-item { display: flex; justify-content: space-between; margin-bottom: 8px; }
.cv-cert-name { font-weight: 600; color: #333; }
.cv-cert-date { color: #888; font-size: 0.85rem; }
.cv-hobbies { display: flex; flex-wrap: wrap; gap: 8px; }
.cv-hobby { background: #1a1a2e; color: white; padding: 6px 14px; border-radius: 15px; font-size: 0.8rem; }
.cv-lang-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee; }
.cv-family-section { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.cv-family-item { background: #f5f5f5; padding: 10px; border-radius: 6px; }
.cv-family-label { font-weight: bold; color: #1a1a2e; font-size: 0.85rem; }
.cv-family-value { color: #555; font-size: 0.9rem; }
.cv-declaration { background: #f9f9f9; padding: 15px; border-radius: 6px; border-left: 3px solid #e94560; font-size: 0.9rem; color: #555; line-height: 1.6; }

/* Print Styles */
@media print {
    body { background: white; padding: 0; }
    .form-box, .progress, header, .btns, .container > header, .container > .progress { display: none !important; }
    .preview { display: block !important; margin: 0; }
    .cv-paper { box-shadow: none; max-width: 100%; }
    .cv-container { display: flex; }
    .cv-sidebar { background: #1a1a2e !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .cv-sidebar-skill, .cv-hobby { background: rgba(255,255,255,0.1) !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .cv-section h2 { border-bottom-color: #e94560 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .cv-entry, .cv-project, .cv-declaration { border-left-color: #e94560 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
</head>
<body>
<div class="container">
<header><h1>Professional CV Builder <span>By Himanshu</span></h1></header>
<div class="progress">
<div class="step {% if current_step >= 0 %}active{% endif %}">1. Personal</div>
<div class="step {% if current_step >= 1 %}active{% endif %}">2. Summary</div>
<div class="step {% if current_step >= 2 %}active{% endif %}">3. Education</div>
<div class="step {% if current_step >= 3 %}active{% endif %}">4. Skills</div>
<div class="step {% if current_step >= 4 %}active{% endif %}">5. Experience</div>
<div class="step {% if current_step >= 5 %}active{% endif %}">6. Projects</div>
<div class="step {% if current_step >= 6 %}active{% endif %}">7. More</div>
<div class="step {% if current_step >= 7 %}active{% endif %}">8. Preview</div>
</div>
<form method="POST" enctype="multipart/form-data" class="form-box">
<!-- Step 1: Personal Details -->
<div class="form-section {% if current_step == 0 %}active{% endif %}">
<h3> Personal Details</h3>
<div class="photo-area">
{% if data.photo %}<img src="{{ data.photo }}" class="photo-preview">{% endif %}
<label class="file-upload">
 Upload Profile Photo
<input type="file" name="photo" accept="image/*" onchange="previewPhoto(this)">
</label>
</div>
<div class="form-row">
<div class="form-group"><label>Full Name *</label><input type="text" name="name" value="{{ data.name or '' }}" required placeholder="John Doe"></div>
<div class="form-group"><label>Date of Birth</label><input type="date" name="dob" value="{{ data.dob or '' }}"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Email *</label><input type="email" name="email" value="{{ data.email or '' }}" required placeholder="john@example.com"></div>
<div class="form-group"><label>Phone *</label><input type="tel" name="phone" value="{{ data.phone or '' }}" required placeholder="+91 9876543210"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Address</label><input type="text" name="address" value="{{ data.address or '' }}" placeholder="City, State, Country"></div>
<div class="form-group"><label>LinkedIn URL</label><input type="url" name="linkedin" value="{{ data.linkedin or '' }}" placeholder="https://linkedin.com/in/johndoe"></div>
</div>
<div class="form-row">
<div class="form-group"><label>GitHub</label><input type="url" name="github" value="{{ data.github or '' }}" placeholder="https://github.com/johndoe"></div>
<div class="form-group"><label>Portfolio Website</label><input type="url" name="website" value="{{ data.website or '' }}" placeholder="https://johndoe.com"></div>
</div>
</div>

<!-- Step 2: Career Objective -->
<div class="form-section {% if current_step == 1 %}active{% endif %}">
<h3> Career Objective & Summary</h3>
<div class="form-group"><label>Career Objective</label><textarea name="objective" placeholder="Brief career goal...">{{ data.objective or '' }}</textarea></div>
<div class="form-group"><label>Professional Summary</label><textarea name="summary" placeholder="Write about your skills, experience, and what you bring to the role...">{{ data.summary or '' }}</textarea></div>
</div>

<!-- Step 3: Education -->
<div class="form-section {% if current_step == 2 %}active{% endif %}">
<h3> Education</h3>
<div class="entry">
<h4 style="color:#1a1a2e;margin-bottom:10px;">Graduation / Bachelor's Degree</h4>
<div class="form-row">
<div class="form-group"><label>Degree</label><input type="text" name="grad_degree" value="{{ data.grad_degree or '' }}" placeholder="B.Tech in Computer Science"></div>
<div class="form-group"><label>Institution</label><input type="text" name="grad_school" value="{{ data.grad_school or '' }}" placeholder="University Name"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Year of Passing</label><input type="text" name="grad_year" value="{{ data.grad_year or '' }}" placeholder="2020-2024"></div>
<div class="form-group"><label>Percentage / CGPA</label><input type="text" name="grad_cgpa" value="{{ data.grad_cgpa or '' }}" placeholder="8.5 CGPA"></div>
</div>
</div>
<div class="entry">
<h4 style="color:#1a1a2e;margin-bottom:10px;">12th / Senior Secondary</h4>
<div class="form-row">
<div class="form-group"><label>Stream</label><input type="text" name="twelve_stream" value="{{ data.twelve_stream or '' }}" placeholder="Science (PCM/PCB)"></div>
<div class="form-group"><label>School</label><input type="text" name="twelve_school" value="{{ data.twelve_school or '' }}" placeholder="School Name"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Year</label><input type="text" name="twelve_year" value="{{ data.twelve_year or '' }}" placeholder="2018-2020"></div>
<div class="form-group"><label>Percentage</label><input type="text" name="twelve_percentage" value="{{ data.twelve_percentage or '' }}" placeholder="85%"></div>
</div>
</div>
<div class="entry">
<h4 style="color:#1a1a2e;margin-bottom:10px;">10th / Secondary</h4>
<div class="form-row">
<div class="form-group"><label>School</label><input type="text" name="ten_school" value="{{ data.ten_school or '' }}" placeholder="School Name"></div>
<div class="form-group"><label>Board</label><input type="text" name="ten_board" value="{{ data.ten_board or '' }}" placeholder="CBSE/ICSE/State Board"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Year</label><input type="text" name="ten_year" value="{{ data.ten_year or '' }}" placeholder="2016-2018"></div>
<div class="form-group"><label>Percentage</label><input type="text" name="ten_percentage" value="{{ data.ten_percentage or '' }}" placeholder="90%"></div>
</div>
</div>
</div>

<!-- Step 4: Skills -->
<div class="form-section {% if current_step == 3 %}active{% endif %}">
<h3> Skills</h3>
<div class="form-group"><label>Technical Skills (comma separated)</label><textarea name="tech_skills" placeholder="Python, Java, JavaScript, React, Node.js, SQL, Git, Docker...">{{ data.tech_skills or '' }}</textarea></div>
<div class="form-group"><label>Soft Skills (comma separated)</label><textarea name="soft_skills" placeholder="Leadership, Communication, Problem Solving, Teamwork...">{{ data.soft_skills or '' }}</textarea></div>
</div>

<!-- Step 5: Experience -->
<div class="form-section {% if current_step == 4 %}active{% endif %}">
<h3> Experience & Internships</h3>
{% for job in data.experience %}
<div class="entry">
<div class="form-row">
<div class="form-group"><label>Job Title / Role</label><input type="text" name="job_title_{{ loop.index0 }}" value="{{ job.title }}"></div>
<div class="form-group"><label>Company / Organization</label><input type="text" name="company_{{ loop.index0 }}" value="{{ job.company }}"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Start Date</label><input type="text" name="job_start_{{ loop.index0 }}" value="{{ job.start }}" placeholder="Jan 2023"></div>
<div class="form-group"><label>End Date</label><input type="text" name="job_end_{{ loop.index0 }}" value="{{ job.end }}" placeholder="Present / Dec 2023"></div>
</div>
<div class="form-group"><label>Description / Key Responsibilities</label><textarea name="job_desc_{{ loop.index0 }}">{{ job.description }}</textarea></div>
</div>
{% endfor %}
<button type="button" class="btn btn-add" onclick="addExp()"> Add Experience</button>
<div id="new-exp"></div>
</div>

<!-- Step 6: Projects -->
<div class="form-section {% if current_step == 5 %}active{% endif %}">
<h3> Projects</h3>
{% for proj in data.projects %}
<div class="entry">
<div class="form-row">
<div class="form-group"><label>Project Title</label><input type="text" name="proj_title_{{ loop.index0 }}" value="{{ proj.title }}"></div>
<div class="form-group"><label>Technologies Used</label><input type="text" name="proj_tech_{{ loop.index0 }}" value="{{ proj.tech }}" placeholder="Python, Django, MySQL"></div>
</div>
<div class="form-group"><label>Description</label><textarea name="proj_desc_{{ loop.index0 }}">{{ proj.description }}</textarea></div>
</div>
{% endfor %}
<button type="button" class="btn btn-add" onclick="addProj()"> Add Project</button>
<div id="new-proj"></div>
</div>

<!-- Step 7: More Sections -->
<div class="form-section {% if current_step == 6 %}active{% endif %}">
<h3> More Details</h3>
<div class="form-group"><label>Certifications (one per line)</label><textarea name="certifications" placeholder="AWS Certified Developer - Amazon - 2023&#10;Python for Data Science - Coursera - 2022">{{ data.certifications or '' }}</textarea></div>
<div class="form-group"><label>Achievements (one per line)</label><textarea name="achievements" placeholder="Won hackathon 2023 - 1st place&#10;Published research paper on AI">{{ data.achievements or '' }}</textarea></div>
<div class="form-group"><label>Hobbies & Interests (comma separated)</label><input type="text" name="hobbies" value="{{ data.hobbies or '' }}" placeholder="Reading, Photography, Cricket, Gaming"></div>
<div class="form-group"><label>Languages Known (comma separated)</label><input type="text" name="languages" value="{{ data.languages or '' }}" placeholder="English (Fluent), Hindi (Native), Spanish (Basic)"></div>
<div class="form-row">
<div class="form-group"><label>Father's Name</label><input type="text" name="father_name" value="{{ data.father_name or '' }}" placeholder="Father's Name"></div>
<div class="form-group"><label>Mother's Name</label><input type="text" name="mother_name" value="{{ data.mother_name or '' }}" placeholder="Mother's Name"></div>
</div>
<div class="form-group"><label>Declaration</label><textarea name="declaration" placeholder="I hereby declare that all the information given above is true and correct to the best of my knowledge...">{{ data.declaration or 'I hereby declare that all the information given above is true and correct to the best of my knowledge.' }}</textarea></div>
</div>

<!-- Navigation Buttons -->
<div class="btns">
<div>{% if current_step > 0 %}<button type="submit" name="action" value="prev" class="btn btn-secondary"> Previous</button>{% endif %}</div>
<div>{% if current_step < 7 %}<button type="submit" name="action" value="next" class="btn btn-primary">Next </button>{% endif %}{% if current_step == 7 %}<button type="button" class="btn btn-success" onclick="window.print()"> Download PDF</button>{% endif %}</div>
</div>
</form>

<!-- CV Preview -->
<div class="preview {% if current_step == 7 %}active{% endif %}">
<div class="cv-paper">
<div class="cv-container">
<!-- Sidebar -->
<div class="cv-sidebar">
<div class="cv-sidebar-photo">
{% if data.photo %}<img src="{{ data.photo }}">{% endif %}
</div>
<div class="cv-sidebar-name">{{ data.name or "Your Name" }}</div>
<div class="cv-sidebar-title">{{ data.objective or "Career Objective" }}</div>

<div class="cv-sidebar-section">
<h4> Contact</h4>
<div class="cv-sidebar-contact">
{% if data.email %}<span><span class="label"></span>{{ data.email }}</span>{% endif %}
{% if data.phone %}<span><span class="label"></span>{{ data.phone }}</span>{% endif %}
{% if data.address %}<span><span class="label"></span>{{ data.address }}</span>{% endif %}
{% if data.linkedin %}<span><span class="label"></span>{{ data.linkedin }}</span>{% endif %}
{% if data.github %}<span><span class="label"></span>{{ data.github }}</span>{% endif %}
{% if data.website %}<span><span class="label"></span>{{ data.website }}</span>{% endif %}
</div>
</div>

<div class="cv-sidebar-section">
<h4> Skills</h4>
<div class="cv-sidebar-skills">
{% if data.tech_skills %}{% for s in data.tech_skills.split(",") %}{% if s.strip() %}<span class="cv-sidebar-skill">{{ s.strip() }}</span>{% endif %}{% endfor %}{% endif %}
{% if data.soft_skills %}{% for s in data.soft_skills.split(",") %}{% if s.strip() %}<span class="cv-sidebar-skill">{{ s.strip() }}</span>{% endif %}{% endfor %}{% endif %}
</div>
</div>

{% if data.languages %}
<div class="cv-sidebar-section">
<h4> Languages</h4>
<div class="cv-sidebar-contact">
{% for lang in data.languages.split(",") %}{% if lang.strip() %}<span>{{ lang.strip() }}</span>{% endif %}{% endfor %}
</div>
</div>
{% endif %}

{% if data.hobbies %}
<div class="cv-sidebar-section">
<h4> Interests</h4>
<div class="cv-sidebar-skills">
{% for h in data.hobbies.split(",") %}{% if h.strip() %}<span class="cv-sidebar-skill">{{ h.strip() }}</span>{% endif %}{% endfor %}
</div>
</div>
{% endif %}
</div>

<!-- Main Content -->
<div class="cv-main">
<div class="cv-main-name">{{ data.name or "Your Name" }}</div>
<div class="cv-main-title">{{ data.objective or "Career Objective" }}</div>

{% if data.summary %}
<div class="cv-section"><h2> Professional Summary</h2><p style="line-height:1.7;color:#555;">{{ data.summary }}</p></div>
{% endif %}

{% if data.grad_degree or data.twelve_school or data.ten_school %}
<div class="cv-section"><h2> Education</h2>
{% if data.grad_degree %}
<div class="cv-entry">
<div class="cv-entry-title">{{ data.grad_degree }}</div>
{% if data.grad_school %}<div class="cv-entry-sub">{{ data.grad_school }}</div>{% endif %}
<div class="cv-entry-date">{{ data.grad_year or '' }}{% if data.grad_cgpa %} | {{ data.grad_cgpa }}{% endif %}</div>
</div>
{% endif %}
{% if data.twelve_stream %}
<div class="cv-entry">
<div class="cv-entry-title">12th - {{ data.twelve_stream }}</div>
{% if data.twelve_school %}<div class="cv-entry-sub">{{ data.twelve_school }}</div>{% endif %}
<div class="cv-entry-date">{{ data.twelve_year or '' }}{% if data.twelve_percentage %} | {{ data.twelve_percentage }}{% endif %}</div>
</div>
{% endif %}
{% if data.ten_school %}
<div class="cv-entry">
<div class="cv-entry-title">10th</div>
<div class="cv-entry-sub">{{ data.ten_school }}{% if data.ten_board %} ({{ data.ten_board }}){% endif %}</div>
<div class="cv-entry-date">{{ data.ten_year or '' }}{% if data.ten_percentage %} | {{ data.ten_percentage }}{% endif %}</div>
</div>
{% endif %}
</div>
{% endif %}

{% if data.experience %}
<div class="cv-section"><h2> Experience</h2>
{% for job in data.experience %}
<div class="cv-entry">
<div class="cv-entry-title">{{ job.title }}</div>
{% if job.company %}<div class="cv-entry-sub">{{ job.company }}</div>{% endif %}
{% if job.start %}<div class="cv-entry-date">{{ job.start }}{% if job.end %} - {{ job.end }}{% endif %}</div>{% endif %}
{% if job.description %}<div class="cv-entry-desc">{{ job.description }}</div>{% endif %}
</div>
{% endfor %}
</div>
{% endif %}

{% if data.projects %}
<div class="cv-section"><h2> Projects</h2>
{% for proj in data.projects %}
<div class="cv-project">
<div class="cv-project-title">{{ proj.title }}</div>
{% if proj.tech %}<div class="cv-project-tech">Tech: {{ proj.tech }}</div>{% endif %}
{% if proj.description %}<div class="cv-project-desc">{{ proj.description }}</div>{% endif %}
</div>
{% endfor %}
</div>
{% endif %}

{% if data.certifications %}
<div class="cv-section"><h2> Certifications</h2>
{% for cert in data.certifications.split(chr(10)) %}{% if cert.strip() %}
{% set parts = cert.split(" - ") %}
<div class="cv-cert-item">
<div class="cv-cert-name">{{ parts[0] }}</div>
<div class="cv-cert-date">{% if parts[1] %}{{ parts[1] }}{% endif %}{% if parts[2] %} - {{ parts[2] }}{% endif %}</div>
</div>
{% endif %}{% endfor %}
</div>
{% endif %}

{% if data.achievements %}
<div class="cv-section"><h2> Achievements</h2>
{% for ach in data.achievements.split(chr(10)) %}{% if ach.strip() %}
<div class="cv-entry"><div class="cv-entry-desc">{{ ach }}</div></div>
{% endif %}{% endfor %}
</div>
{% endif %}

{% if data.father_name or data.mother_name %}
<div class="cv-section"><h2> Family Details</h2>
<div class="cv-family-section">
{% if data.father_name %}<div class="cv-family-item"><div class="cv-family-label">Father</div><div class="cv-family-value">{{ data.father_name }}</div></div>{% endif %}
{% if data.mother_name %}<div class="cv-family-item"><div class="cv-family-label">Mother</div><div class="cv-family-value">{{ data.mother_name }}</div></div>{% endif %}
</div>
</div>
{% endif %}

{% if data.declaration %}
<div class="cv-section"><h2> Declaration</h2>
<div class="cv-declaration">{{ data.declaration }}</div>
</div>
{% endif %}
</div>
</div>
</div>
</div>
</div>

<script>
let expC = {{ data.experience|length if data.experience else 0 }};
let projC = {{ data.projects|length if data.projects else 0 }};

function addExp() {
    expC++;
    document.getElementById("new-exp").insertAdjacentHTML("beforeend", '<div class="entry"><div class="form-row"><div class="form-group"><label>Job Title</label><input type="text" name="job_title_new"></div><div class="form-group"><label>Company</label><input type="text" name="company_new"></div></div><div class="form-row"><div class="form-group"><label>Start</label><input type="text" name="job_start_new" placeholder="Jan 2023"></div><div class="form-group"><label>End</label><input type="text" name="job_end_new" placeholder="Present"></div></div><div class="form-group"><label>Description</label><textarea name="job_desc_new"></textarea></div></div>');
}

function addProj() {
    projC++;
    document.getElementById("new-proj").insertAdjacentHTML("beforeend", '<div class="entry"><div class="form-row"><div class="form-group"><label>Project Title</label><input type="text" name="proj_title_new"></div><div class="form-group"><label>Technologies</label><input type="text" name="proj_tech_new" placeholder="Python, Django"></div></div><div class="form-group"><label>Description</label><textarea name="proj_desc_new"></textarea></div></div>');
}

function previewPhoto(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let img = input.parentElement.previousElementSibling;
            if (!img || img.tagName !== "IMG") {
                img = document.createElement("img");
                img.className = "photo-preview";
                input.parentElement.parentElement.insertBefore(img, input.parentElement);
            }
            img.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}
</script>
</body>
</html>"""

@app.route("/", methods=["GET", "POST"])
def index():
    global cv_data, current_step
    if request.method == "GET":
        current_step = 0
        cv_data = {}
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "next":
            current_step = min(current_step + 1, 7)
        elif action == "prev":
            current_step = max(current_step - 1, 0)
        
        cv_data = {
            "name": request.form.get("name", ""),
            "dob": request.form.get("dob", ""),
            "email": request.form.get("email", ""),
            "phone": request.form.get("phone", ""),
            "address": request.form.get("address", ""),
            "linkedin": request.form.get("linkedin", ""),
            "github": request.form.get("github", ""),
            "website": request.form.get("website", ""),
            "objective": request.form.get("objective", ""),
            "summary": request.form.get("summary", ""),
            "grad_degree": request.form.get("grad_degree", ""),
            "grad_school": request.form.get("grad_school", ""),
            "grad_year": request.form.get("grad_year", ""),
            "grad_cgpa": request.form.get("grad_cgpa", ""),
            "twelve_stream": request.form.get("twelve_stream", ""),
            "twelve_school": request.form.get("twelve_school", ""),
            "twelve_year": request.form.get("twelve_year", ""),
            "twelve_percentage": request.form.get("twelve_percentage", ""),
            "ten_school": request.form.get("ten_school", ""),
            "ten_board": request.form.get("ten_board", ""),
            "ten_year": request.form.get("ten_year", ""),
            "ten_percentage": request.form.get("ten_percentage", ""),
            "tech_skills": request.form.get("tech_skills", ""),
            "soft_skills": request.form.get("soft_skills", ""),
            "certifications": request.form.get("certifications", ""),
            "achievements": request.form.get("achievements", ""),
            "hobbies": request.form.get("hobbies", ""),
            "languages": request.form.get("languages", ""),
            "father_name": request.form.get("father_name", ""),
            "mother_name": request.form.get("mother_name", ""),
            "declaration": request.form.get("declaration", ""),
            "photo": cv_data.get("photo", ""),
            "experience": [],
            "projects": []
        }
        
        # Handle photo upload
        if "photo" in request.files:
            f = request.files["photo"]
            if f.filename:
                os.makedirs("static/uploads", exist_ok=True)
                fp = "static/uploads/photo.jpg"
                f.save(fp)
                cv_data["photo"] = "/" + fp
        
        # Parse experience
        for k in request.form:
            if k.startswith("job_title_"):
                i = k.split("_")[-1]
                if i != "new":
                    cv_data["experience"].append({
                        "title": request.form.get(f"job_title_{i}", ""),
                        "company": request.form.get(f"company_{i}", ""),
                        "start": request.form.get(f"job_start_{i}", ""),
                        "end": request.form.get(f"job_end_{i}", ""),
                        "description": request.form.get(f"job_desc_{i}", "")
                    })
        if request.form.get("job_title_new"):
            cv_data["experience"].append({
                "title": request.form.get("job_title_new", ""),
                "company": request.form.get("company_new", ""),
                "start": request.form.get("job_start_new", ""),
                "end": request.form.get("job_end_new", ""),
                "description": request.form.get("job_desc_new", "")
            })
        
        # Parse projects
        for k in request.form:
            if k.startswith("proj_title_"):
                i = k.split("_")[-1]
                if i != "new":
                    cv_data["projects"].append({
                        "title": request.form.get(f"proj_title_{i}", ""),
                        "tech": request.form.get(f"proj_tech_{i}", ""),
                        "description": request.form.get(f"proj_desc_{i}", "")
                    })
        if request.form.get("proj_title_new"):
            cv_data["projects"].append({
                "title": request.form.get("proj_title_new", ""),
                "tech": request.form.get("proj_tech_new", ""),
                "description": request.form.get("proj_desc_new", "")
            })
        
        # Save to database
        if cv_data.get("name") and cv_data.get("email"):
            conn = sqlite3.connect("cv.db")
            conn.execute("INSERT INTO users (name, email) VALUES (?, ?)", (cv_data["name"], cv_data["email"]))
            conn.commit()
            conn.close()
    
    return render_template_string(TEMPLATE, data=cv_data, current_step=current_step)

if __name__ == "__main__":
 import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    
