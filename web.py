from flask import Flask, render_template_string, request
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "cv_builder_secret_key"

cv_data = {}
current_step = 0
cv_template = "modern"

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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
body { font-family: 'Poppins', 'Segoe UI', sans-serif; background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 50%, #b8c6db 100%); min-height: 100vh; padding: 2rem; transition: all 0.3s ease; }
.container { max-width: 900px; margin: 0 auto; }
header { text-align: center; color: #1a365d; margin-bottom: 2rem; }
header h1 { font-size: 2.4rem; font-weight: 700; letter-spacing: 1px; text-shadow: 0 2px 10px rgba(26, 54, 93, 0.1); }
header span { color: #4a90d9; font-weight: 700; }
.progress { display: flex; justify-content: center; gap: 0.6rem; margin-bottom: 2.5rem; flex-wrap: wrap; }
.step { padding: 0.7rem 1.2rem; background: rgba(255,255,255,0.6); color: #4a5568; border-radius: 25px; font-size: 0.85rem; transition: all 0.25s ease; font-weight: 500; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.step.active { background: linear-gradient(135deg, #4a90d9, #667eea); color: white; transform: scale(1.08); box-shadow: 0 6px 20px rgba(74, 144, 217, 0.5); }
.form-box { background: white; border-radius: 24px; padding: 3rem; box-shadow: 0 20px 60px rgba(26, 54, 93, 0.12), 0 4px 12px rgba(0,0,0,0.05), 0 0 0 1px rgba(74, 144, 217, 0.05); }
.form-section { display: none; }
.form-section.active { display: block; animation: fadeIn 0.4s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.form-section h3 { color: #1a365d; margin-bottom: 1.8rem; border-bottom: 3px solid #4a90d9; padding-bottom: 0.8rem; font-size: 1.3rem; display: flex; align-items: center; gap: 12px; font-weight: 700; letter-spacing: 0.5px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
.form-group { margin-bottom: 1.4rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #2d3748; font-size: 0.9rem; }
.form-group input, .form-group textarea, .form-group select { width: 100%; padding: 1rem 1.2rem; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 0.95rem; transition: all 0.25s ease; font-family: 'Poppins', sans-serif; background: #fafbfc; }
.form-group input:focus, .form-group textarea:focus, .form-group select:focus { border-color: #4a90d9; outline: none; box-shadow: 0 0 0 4px rgba(74, 144, 217, 0.2), 0 4px 12px rgba(74, 144, 217, 0.1); background: white; }
.form-group input::placeholder, .form-group textarea::placeholder { color: #a0aec0; }
.form-group textarea { min-height: 90px; resize: vertical; }
.entry { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.5rem; border-radius: 14px; margin-bottom: 1.2rem; border-left: 5px solid #4a90d9; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.photo-area { text-align: center; margin-bottom: 1.5rem; }
.photo-preview { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 5px solid #4a90d9; box-shadow: 0 8px 25px rgba(74, 144, 217, 0.35), 0 0 0 3px rgba(74, 144, 217, 0.1); transition: all 0.3s ease; }
.file-upload { display: inline-block; padding: 0.8rem 1.8rem; background: linear-gradient(135deg, #4a90d9, #667eea); color: white; border-radius: 30px; cursor: pointer; font-weight: 600; transition: all 0.25s ease; font-size: 0.9rem; letter-spacing: 0.5px; }
.file-upload:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 8px 25px rgba(74, 144, 217, 0.5); }
.file-upload input { display: none; }
.btns { display: flex; justify-content: space-between; margin-top: 2.5rem; gap: 1.2rem; flex-wrap: wrap; }
.btn { padding: 1rem 2rem; border: none; border-radius: 30px; cursor: pointer; font-weight: 600; font-size: 1rem; transition: all 0.25s ease; font-family: 'Poppins', sans-serif; letter-spacing: 0.5px; }
.btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.btn-primary { background: linear-gradient(135deg, #4a90d9 0%, #667eea 100%); color: white; }
.btn-primary:hover { box-shadow: 0 12px 30px rgba(74, 144, 217, 0.45); }
.btn-secondary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.btn-secondary:hover { box-shadow: 0 12px 30px rgba(102, 126, 234, 0.45); }
.btn-success { background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); color: white; }
.btn-success:hover { box-shadow: 0 12px 30px rgba(72, 187, 120, 0.45); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-add { background: linear-gradient(135deg, #4a90d9 0%, #667eea 100%); color: white; padding: 0.7rem 1.4rem; font-size: 0.9rem; border-radius: 25px; }
.btn-add:hover { box-shadow: 0 8px 20px rgba(74, 144, 217, 0.45); transform: translateY(-2px); }

/* Template Selector */
.template-selector { text-align: center; margin-bottom: 1.5rem; }
.template-selector label { display: block; font-weight: 600; color: #1a365d; margin-bottom: 0.8rem; font-size: 1rem; }
.template-options { display: flex; justify-content: center; gap: 0.8rem; flex-wrap: wrap; }
.template-btn { padding: 0.6rem 1.2rem; border: 2px solid #e2e8f0; background: white; border-radius: 20px; cursor: pointer; font-weight: 600; font-size: 0.85rem; color: #4a5568; transition: all 0.25s ease; font-family: 'Poppins', sans-serif; }
.template-btn:hover { border-color: #4a90d9; color: #4a90d9; }
.template-btn.active { background: linear-gradient(135deg, #4a90d9, #667eea); color: white; border-color: transparent; box-shadow: 0 4px 15px rgba(74, 144, 217, 0.4); }

/* Form Validation */
.form-group.error input, .form-group.error textarea { border-color: #e53e3e !important; }
.form-group.error input:focus, .form-group.error textarea:focus { box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.2) !important; }
.error-message { color: #e53e3e; font-size: 0.8rem; margin-top: 4px; display: none; }
.form-group.error .error-message { display: block; }
.form-error-banner { background: #fed7d7; border: 1px solid #fc8181; color: #c53030; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; }

/* ==================== TEMPLATE: MODERN ==================== */
.template-modern .cv-paper { background: white; max-width: 850px; margin: 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.15); border-radius: 8px; overflow: hidden; }
.template-modern .cv-header { background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); color: white; padding: 40px 40px 30px; text-align: center; }
.template-modern .cv-header-name { font-size: 2.5rem; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; }
.template-modern .cv-header-title { font-size: 1.1rem; color: #90cdf4; font-weight: 400; margin-bottom: 20px; }
.template-modern .cv-header-contact { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; font-size: 0.85rem; color: #e2e8f0; }
.template-modern .cv-header-contact span { display: flex; align-items: center; gap: 6px; }
.template-modern .cv-body { display: flex; }
.template-modern .cv-left { width: 280px; background: #f7fafc; padding: 30px 25px; flex-shrink: 0; border-right: 1px solid #e2e8f0; }
.template-modern .cv-right { flex: 1; padding: 30px 35px; background: white; }
.template-modern .cv-left-section h3 { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #2c5282; margin-bottom: 12px; }
.template-modern .cv-right-section h2 { font-size: 1.05rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #1a365d; margin-bottom: 15px; padding-bottom: 6px; border-bottom: 2px solid #4a90d9; }
.template-modern .cv-skill-item { display: inline-block; background: white; border: 1px solid #cbd5e0; padding: 5px 12px; border-radius: 4px; font-size: 0.8rem; color: #2d3748; margin: 3px 3px; }
.template-modern .cv-hobby-item { display: inline-block; background: #2c5282; color: white; padding: 4px 10px; border-radius: 3px; font-size: 0.75rem; margin: 3px 3px; }
.template-modern .cv-project { background: #f7fafc; padding: 12px 15px; border-radius: 5px; margin-bottom: 12px; border-left: 3px solid #4a90d9; }
.template-modern .cv-declaration { background: #f7fafc; padding: 15px; border-radius: 5px; border-left: 3px solid #4a90d9; }

/* ==================== TEMPLATE: CLASSIC ==================== */
.template-classic .cv-paper { background: white; max-width: 850px; margin: 0 auto; box-shadow: 0 5px 20px rgba(0,0,0,0.1); border: 1px solid #ddd; }
.template-classic .cv-header { background: #2c3e50; color: white; padding: 30px 40px; text-align: center; border-bottom: 4px solid #3498db; }
.template-classic .cv-header-name { font-size: 2.2rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px; }
.template-classic .cv-header-title { font-size: 1rem; color: #bdc3c7; font-weight: 400; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
.template-classic .cv-header-contact { display: flex; justify-content: center; gap: 25px; font-size: 0.8rem; color: #ecf0f1; }
.template-classic .cv-header-contact span { display: flex; align-items: center; gap: 5px; }
.template-classic .cv-body { display: flex; }
.template-classic .cv-left { width: 220px; background: #ecf0f1; padding: 25px 20px; flex-shrink: 0; }
.template-classic .cv-right { flex: 1; padding: 25px 30px; }
.template-classic .cv-left-section { margin-bottom: 20px; }
.template-classic .cv-left-section h3 { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #2c3e50; margin-bottom: 10px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
.template-classic .cv-right-section { margin-bottom: 20px; }
.template-classic .cv-right-section h2 { font-size: 1rem; font-weight: 700; text-transform: uppercase; color: #2c3e50; margin-bottom: 12px; border-bottom: 1px solid #3498db; padding-bottom: 4px; }
.template-classic .cv-skill-item { display: block; background: white; padding: 4px 8px; border-radius: 3px; font-size: 0.75rem; color: #2c3e50; margin: 4px 0; border-left: 3px solid #3498db; }
.template-classic .cv-hobby-item { display: block; background: #2c3e50; color: white; padding: 4px 8px; border-radius: 3px; font-size: 0.7rem; margin: 4px 0; }
.template-classic .cv-project { background: #ecf0f1; padding: 10px; margin-bottom: 10px; border: 1px solid #bdc3c7; }
.template-classic .cv-declaration { background: #ecf0f1; padding: 12px; border: 1px solid #bdc3c7; }

/* ==================== TEMPLATE: MINIMAL ==================== */
.template-minimal .cv-paper { background: white; max-width: 800px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.template-minimal .cv-header { background: white; color: #111; padding: 40px 40px 20px; text-align: center; border-bottom: 2px solid #111; }
.template-minimal .cv-header-name { font-size: 2.4rem; font-weight: 300; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 5px; }
.template-minimal .cv-header-title { font-size: 0.9rem; color: #666; font-weight: 400; margin-bottom: 15px; }
.template-minimal .cv-header-contact { display: flex; justify-content: center; gap: 20px; font-size: 0.8rem; color: #333; }
.template-minimal .cv-header-contact span { display: flex; align-items: center; gap: 5px; }
.template-minimal .cv-body { display: flex; }
.template-minimal .cv-left { width: 200px; padding: 25px 20px; flex-shrink: 0; }
.template-minimal .cv-right { flex: 1; padding: 25px 30px; }
.template-minimal .cv-left-section { margin-bottom: 20px; }
.template-minimal .cv-left-section h3 { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #111; margin-bottom: 8px; letter-spacing: 2px; }
.template-minimal .cv-right-section { margin-bottom: 18px; }
.template-minimal .cv-right-section h2 { font-size: 0.9rem; font-weight: 600; text-transform: uppercase; color: #111; margin-bottom: 10px; letter-spacing: 1px; }
.template-minimal .cv-skill-item { display: inline-block; background: #f5f5f5; padding: 3px 10px; font-size: 0.75rem; color: #333; margin: 2px; }
.template-minimal .cv-hobby-item { display: inline-block; background: #111; color: white; padding: 3px 10px; font-size: 0.7rem; margin: 2px; }
.template-minimal .cv-project { padding: 8px 0; margin-bottom: 10px; border-bottom: 1px solid #eee; }
.template-minimal .cv-declaration { padding: 10px 0; border-left: none; border-bottom: 1px solid #eee; }

/* ==================== TEMPLATE: ELEGANT ==================== */
.template-elegant .cv-paper { background: white; max-width: 850px; margin: 0 auto; box-shadow: 0 15px 50px rgba(0,0,0,0.12); border-radius: 4px; overflow: hidden; }
.template-elegant .cv-header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 50px 50px 40px; text-align: center; }
.template-elegant .cv-header-name { font-size: 2.8rem; font-weight: 300; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 8px; font-family: 'Georgia', serif; }
.template-elegant .cv-header-title { font-size: 1rem; color: #e94560; font-weight: 400; margin-bottom: 25px; letter-spacing: 2px; text-transform: uppercase; }
.template-elegant .cv-header-contact { display: flex; justify-content: center; gap: 25px; font-size: 0.8rem; color: #ccc; }
.template-elegant .cv-header-contact span { display: flex; align-items: center; gap: 6px; }
.template-elegant .cv-body { display: flex; }
.template-elegant .cv-left { width: 260px; background: #fafafa; padding: 30px 25px; flex-shrink: 0; border-right: 1px solid #e0e0e0; }
.template-elegant .cv-right { flex: 1; padding: 30px 35px; background: white; }
.template-elegant .cv-left-section { margin-bottom: 25px; }
.template-elegant .cv-left-section h3 { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #1a1a2e; margin-bottom: 12px; letter-spacing: 2px; border-bottom: 2px solid #e94560; padding-bottom: 6px; }
.template-elegant .cv-right-section { margin-bottom: 22px; }
.template-elegant .cv-right-section h2 { font-size: 1rem; font-weight: 600; text-transform: uppercase; color: #1a1a2e; margin-bottom: 12px; letter-spacing: 1px; border-bottom: 2px solid #e94560; padding-bottom: 5px; }
.template-elegant .cv-skill-item { display: inline-block; background: white; border: 1px solid #ddd; padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; color: #333; margin: 3px; }
.template-elegant .cv-hobby-item { display: inline-block; background: #1a1a2e; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.7rem; margin: 3px; }
.template-elegant .cv-project { background: #fafafa; padding: 12px 15px; margin-bottom: 12px; border-left: 3px solid #e94560; }
.template-elegant .cv-declaration { background: #fafafa; padding: 15px; border-left: 3px solid #e94560; }

/* CV Preview - Modern Professional Resume */
.preview { display: none; margin-top: 2rem; }
.preview.active { display: block; }
.cv-paper { background: white; max-width: 850px; margin: 0 auto; box-shadow: 0 10px 40px rgba(0,0,0,0.15); border-radius: 8px; overflow: hidden; }
.cv-header { background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); color: white; padding: 40px 40px 30px; text-align: center; }
.cv-header-name { font-size: 2.5rem; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; }
.cv-header-title { font-size: 1.1rem; color: #90cdf4; font-weight: 400; margin-bottom: 20px; }
.cv-header-contact { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; font-size: 0.85rem; color: #e2e8f0; }
.cv-header-contact span { display: flex; align-items: center; gap: 6px; }
.cv-body { display: flex; }
.cv-left { width: 280px; background: #f7fafc; padding: 30px 25px; flex-shrink: 0; border-right: 1px solid #e2e8f0; }
.cv-right { flex: 1; padding: 30px 35px; background: white; }
.cv-section-title { font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #1a365d; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #4a90d9; }
.cv-left-section { margin-bottom: 30px; }
.cv-left-section h3 { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #2c5282; margin-bottom: 12px; }
.cv-contact-item { font-size: 0.8rem; color: #4a5568; margin-bottom: 8px; word-break: break-all; }
.cv-skill-item { display: inline-block; background: white; border: 1px solid #cbd5e0; padding: 5px 12px; border-radius: 4px; font-size: 0.8rem; color: #2d3748; margin: 3px 3px; }
.cv-lang-item { font-size: 0.85rem; color: #4a5568; padding: 4px 0; border-bottom: 1px solid #e2e8f0; }
.cv-hobby-item { display: inline-block; background: #2c5282; color: white; padding: 4px 10px; border-radius: 3px; font-size: 0.75rem; margin: 3px 3px; }
.cv-right-section { margin-bottom: 28px; }
.cv-right-section h2 { font-size: 1.05rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #1a365d; margin-bottom: 15px; padding-bottom: 6px; border-bottom: 2px solid #4a90d9; }
.cv-entry { margin-bottom: 18px; }
.cv-entry-title { font-weight: 700; color: #1a202c; font-size: 0.95rem; }
.cv-entry-sub { color: #4a5568; font-size: 0.9rem; }
.cv-entry-date { color: #718096; font-size: 0.8rem; margin-bottom: 6px; }
.cv-entry-desc { color: #4a5568; line-height: 1.6; font-size: 0.85rem; }
.cv-project { background: #f7fafc; padding: 12px 15px; border-radius: 5px; margin-bottom: 12px; border-left: 3px solid #4a90d9; }
.cv-project-title { font-weight: 700; color: #1a202c; font-size: 0.9rem; }
.cv-project-tech { color: #4a90d9; font-size: 0.8rem; margin: 4px 0; }
.cv-project-desc { color: #4a5568; font-size: 0.85rem; line-height: 1.5; }
.cv-cert-item { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #e2e8f0; }
.cv-cert-name { font-weight: 600; color: #2d3748; font-size: 0.85rem; }
.cv-cert-date { color: #718096; font-size: 0.8rem; }
.cv-family-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.cv-family-item { background: #f7fafc; padding: 10px; border-radius: 4px; }
.cv-family-label { font-weight: 600; color: #2c5282; font-size: 0.8rem; }
.cv-family-value { color: #4a5568; font-size: 0.85rem; }
.cv-declaration { background: #f7fafc; padding: 15px; border-radius: 5px; border-left: 3px solid #4a90d9; font-size: 0.85rem; color: #4a5568; line-height: 1.6; }

/* Print Styles */
@media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    body { 
        background: white !important; 
        padding: 0 !important; 
        margin: 0 !important;
        font-size: 11pt;
    }
    .container { 
        max-width: 100% !important; 
        margin: 0 !important; 
        padding: 0 !important; 
    }
    header, .progress, .form-box, .btns, .photo-area, .file-upload, .btn, .btn-add {
        display: none !important;
    }
    .preview { 
        display: block !important; 
        margin: 0 !important; 
        padding: 0 !important;
    }
    .cv-paper { 
        box-shadow: none !important; 
        border-radius: 0 !important; 
        max-width: 100% !important;
        margin: 0 !important;
        page-break-inside: avoid;
    }
    .cv-body { 
        display: flex !important; 
    }
    .cv-header { 
        background: #1a365d !important; 
        padding: 25px 30px 20px !important;
    }
    .cv-header-name { 
        font-size: 22pt !important; 
        margin-bottom: 5px !important;
    }
    .cv-header-title { 
        font-size: 10pt !important; 
        margin-bottom: 12px !important;
    }
    .cv-header-contact { 
        font-size: 9pt !important; 
        gap: 15px !important;
    }
    .cv-left { 
        width: 240px !important; 
        padding: 20px !important;
        background: #f8fafc !important;
    }
    .cv-right { 
        padding: 20px 25px !important; 
    }
    .cv-left-section { 
        margin-bottom: 18px !important; 
    }
    .cv-left-section h3 { 
        font-size: 9pt !important; 
        margin-bottom: 8px !important;
    }
    .cv-right-section { 
        margin-bottom: 16px !important; 
    }
    .cv-right-section h2 { 
        font-size: 10pt !important; 
        margin-bottom: 10px !important;
    }
    .cv-entry { 
        margin-bottom: 10px !important; 
    }
    .cv-entry-title { 
        font-size: 10pt !important; 
    }
    .cv-entry-sub { 
        font-size: 9pt !important; 
    }
    .cv-entry-date { 
        font-size: 8pt !important; 
    }
    .cv-entry-desc { 
        font-size: 9pt !important; 
        line-height: 1.4 !important;
    }
    .cv-project { 
        padding: 8px 10px !important; 
        margin-bottom: 8px !important;
    }
    .cv-project-title { 
        font-size: 9.5pt !important; 
    }
    .cv-project-tech { 
        font-size: 8pt !important; 
    }
    .cv-project-desc { 
        font-size: 9pt !important; 
    }
    .cv-skill-item { 
        font-size: 8pt !important; 
        padding: 3px 8px !important;
    }
    .cv-hobby-item { 
        font-size: 8pt !important; 
        padding: 3px 8px !important;
    }
    .cv-contact-item { 
        font-size: 8pt !important; 
    }
    .cv-lang-item { 
        font-size: 8.5pt !important; 
    }
    .cv-cert-item { 
        font-size: 9pt !important; 
    }
    .cv-family-grid { 
        gap: 8px !important; 
    }
    .cv-family-item { 
        padding: 6px !important; 
    }
    .cv-declaration { 
        font-size: 9pt !important; 
        padding: 10px !important;
    }
    .template-selector { display: none !important; }
    
    /* Template-specific print */
    .template-modern .cv-header { background: #1a365d !important; }
    .template-modern .cv-left { background: #f8fafc !important; }
    .template-modern .cv-right-section h2, .template-modern .cv-left-section h3 { border-bottom-color: #4a90d9 !important; }
    .template-modern .cv-project, .template-modern .cv-declaration { border-left-color: #4a90d9 !important; }
    
    .template-classic .cv-header { background: #2c3e50 !important; border-bottom-color: #3498db !important; }
    .template-classic .cv-left { background: #ecf0f1 !important; }
    .template-classic .cv-right-section h2 { border-bottom-color: #3498db !important; }
    .template-classic .cv-left-section h3 { border-bottom-color: #bdc3c7 !important; }
    
    .template-minimal .cv-header { background: white !important; color: #111 !important; border-bottom-color: #111 !important; }
    .template-minimal .cv-header-name { color: #111 !important; }
    .template-minimal .cv-header-title { color: #666 !important; }
    .template-minimal .cv-header-contact { color: #333 !important; }
    
    .template-elegant .cv-header { background: #1a1a2e !important; }
    .template-elegant .cv-header-title { color: #e94560 !important; }
    .template-elegant .cv-left { background: #fafafa !important; }
    .template-elegant .cv-right-section h2, .template-elegant .cv-left-section h3 { border-bottom-color: #e94560 !important; }
    .template-elegant .cv-project, .template-elegant .cv-declaration { border-left-color: #e94560 !important; }
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
{% if current_step == 7 %}
<div class="template-selector">
<label>Select Template:</label>
<div class="template-options">
<button type="submit" name="action" value="template_modern" class="template-btn {% if cv_template == 'modern' %}active{% endif %}">Modern</button>
<button type="submit" name="action" value="template_classic" class="template-btn {% if cv_template == 'classic' %}active{% endif %}">Classic</button>
<button type="submit" name="action" value="template_minimal" class="template-btn {% if cv_template == 'minimal' %}active{% endif %}">Minimal</button>
<button type="submit" name="action" value="template_elegant" class="template-btn {% if cv_template == 'elegant' %}active{% endif %}">Elegant</button>
</div>
</div>
{% endif %}
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
<div class="cv-paper template-{{ cv_template }}">
<!-- Header -->
<div class="cv-header">
<div class="cv-header-name">{{ data.name or "Your Name" }}</div>
<div class="cv-header-title">{{ data.objective or "Career Objective" }}</div>
<div class="cv-header-contact">
{% if data.email %}<span>✉ {{ data.email }}</span>{% endif %}
{% if data.phone %}<span>📞 {{ data.phone }}</span>{% endif %}
{% if data.address %}<span>📍 {{ data.address }}</span>{% endif %}
{% if data.linkedin %}<span>🔗 LinkedIn</span>{% endif %}
{% if data.github %}<span>💻 GitHub</span>{% endif %}
{% if data.website %}<span>🌐 Website</span>{% endif %}
</div>
</div>

<div class="cv-body">
<!-- Left Column -->
<div class="cv-left">
{% if data.tech_skills or data.soft_skills %}
<div class="cv-left-section">
<h3>Skills</h3>
{% if data.tech_skills %}{% for s in data.tech_skills.split(",") %}{% if s.strip() %}<span class="cv-skill-item">{{ s.strip() }}</span>{% endif %}{% endfor %}{% endif %}
{% if data.soft_skills %}{% for s in data.soft_skills.split(",") %}{% if s.strip() %}<span class="cv-skill-item">{{ s.strip() }}</span>{% endif %}{% endfor %}{% endif %}
</div>
{% endif %}

{% if data.email or data.phone or data.address %}
<div class="cv-left-section">
<h3>Contact</h3>
{% if data.email %}<div class="cv-contact-item">{{ data.email }}</div>{% endif %}
{% if data.phone %}<div class="cv-contact-item">{{ data.phone }}</div>{% endif %}
{% if data.address %}<div class="cv-contact-item">{{ data.address }}</div>{% endif %}
{% if data.linkedin %}<div class="cv-contact-item">{{ data.linkedin }}</div>{% endif %}
{% if data.github %}<div class="cv-contact-item">{{ data.github }}</div>{% endif %}
{% if data.website %}<div class="cv-contact-item">{{ data.website }}</div>{% endif %}
</div>
{% endif %}

{% if data.languages %}
<div class="cv-left-section">
<h3>Languages</h3>
{% for lang in data.languages.split(",") %}{% if lang.strip() %}<div class="cv-lang-item">{{ lang.strip() }}</div>{% endif %}{% endfor %}
</div>
{% endif %}

{% if data.hobbies %}
<div class="cv-left-section">
<h3>Interests</h3>
{% for h in data.hobbies.split(",") %}{% if h.strip() %}<span class="cv-hobby-item">{{ h.strip() }}</span>{% endif %}{% endfor %}
</div>
{% endif %}
</div>

<!-- Right Column -->
<div class="cv-right">
{% if data.summary %}
<div class="cv-right-section"><h2>Professional Summary</h2><p style="line-height:1.7;color:#4a5568;">{{ data.summary }}</p></div>
{% endif %}

{% if data.grad_degree or data.twelve_school or data.ten_school %}
<div class="cv-right-section"><h2>Education</h2>
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
<div class="cv-right-section"><h2>Experience</h2>
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
<div class="cv-right-section"><h2>Projects</h2>
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
<div class="cv-right-section"><h2>Certifications</h2>
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
<div class="cv-right-section"><h2>Achievements</h2>
{% for ach in data.achievements.split(chr(10)) %}{% if ach.strip() %}
<div class="cv-entry"><div class="cv-entry-desc">{{ ach }}</div></div>
{% endif %}{% endfor %}
</div>
{% endif %}

{% if data.father_name or data.mother_name %}
<div class="cv-right-section"><h2>Family Details</h2>
<div class="cv-family-grid">
{% if data.father_name %}<div class="cv-family-item"><div class="cv-family-label">Father</div><div class="cv-family-value">{{ data.father_name }}</div></div>{% endif %}
{% if data.mother_name %}<div class="cv-family-item"><div class="cv-family-label">Mother</div><div class="cv-family-value">{{ data.mother_name }}</div></div>{% endif %}
</div>
</div>
{% endif %}

{% if data.declaration %}
<div class="cv-right-section"><h2>Declaration</h2>
<div class="cv-declaration">{{ data.declaration }}</div>
</div>
{% endif %}
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

function validateForm() {
    let isValid = true;
    const errors = [];
    
    // Clear previous errors
    document.querySelectorAll('.form-group').forEach(g => g.classList.remove('error'));
    document.querySelectorAll('.form-error-banner').forEach(e => e.remove());
    
    // Get current step fields
    const currentStep = {{ current_step }};
    
    if (currentStep === 0) {
        // Step 1: Personal Details - validate required fields
        const name = document.querySelector('input[name="name"]');
        const email = document.querySelector('input[name="email"]');
        const phone = document.querySelector('input[name="phone"]');
        
        if (!name.value.trim()) {
            name.parentElement.classList.add('error');
            name.parentElement.insertAdjacentHTML('beforeend', '<div class="error-message">Name is required</div>');
            errors.push('Name is required');
            isValid = false;
        }
        
        if (!email.value.trim()) {
            email.parentElement.classList.add('error');
            email.parentElement.insertAdjacentHTML('beforeend', '<div class="error-message">Email is required</div>');
            errors.push('Email is required');
            isValid = false;
        } else if (!isValidEmail(email.value)) {
            email.parentElement.classList.add('error');
            email.parentElement.insertAdjacentHTML('beforeend', '<div class="error-message">Please enter a valid email</div>');
            errors.push('Invalid email format');
            isValid = false;
        }
        
        if (!phone.value.trim()) {
            phone.parentElement.classList.add('error');
            phone.parentElement.insertAdjacentHTML('beforeend', '<div class="error-message">Phone is required</div>');
            errors.push('Phone is required');
            isValid = false;
        }
    }
    
    if (!isValid) {
        // Show error banner
        const formBox = document.querySelector('.form-box');
        const banner = document.createElement('div');
        banner.className = 'form-error-banner';
        banner.textContent = 'Please fill in all required fields correctly';
        formBox.insertBefore(banner, formBox.firstChild);
        return false;
    }
    
    return true;
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Add validation to form submission
document.querySelector('form').addEventListener('submit', function(e) {
    const action = document.querySelector('button[name="action"]:focused')?.value || 
                   document.activeElement?.value;
    if (action === 'next' && !validateForm()) {
        e.preventDefault();
    }
});
</script>
</body>
</html>"""

@app.route("/", methods=["GET", "POST"])
def index():
    global cv_data, current_step, cv_template
    if request.method == "GET":
        current_step = 0
        cv_data = {}
        cv_template = "modern"
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "next":
            current_step = min(current_step + 1, 7)
        elif action == "prev":
            current_step = max(current_step - 1, 0)
        elif action == "template_modern":
            cv_template = "modern"
        elif action == "template_classic":
            cv_template = "classic"
        elif action == "template_minimal":
            cv_template = "minimal"
        elif action == "template_elegant":
            cv_template = "elegant"
        
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
    
    return render_template_string(TEMPLATE, data=cv_data, current_step=current_step, cv_template=cv_template)

if __name__ == "__main__":
 import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    
