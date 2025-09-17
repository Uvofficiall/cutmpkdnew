from flask import Flask, render_template, request, redirect, jsonify, flash, session
import os
import sqlite3
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import pytz
import hashlib
import logging
import sys

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Log template and static folder paths
logger.info(f"Template folder: {app.template_folder}")
logger.info(f"Static folder: {app.static_folder}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Templates exist: {os.path.exists('templates')}")
logger.info(f"Index.html exists: {os.path.exists('templates/index.html')}")

# Initialize database if it doesn't exist
def init_db():
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        # Create table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS CUTM (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Reg_No TEXT,
                Name TEXT,
                Sem TEXT,
                Credits TEXT,
                Grade TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize database on startup
init_db()

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
MONGO_URI = os.getenv('MONGO_URI')

try:
    client = MongoClient(MONGO_URI) if MONGO_URI else None
except:
    client = None

def convert_to_ist(gmt_time):
    ist_timezone = pytz.timezone('Asia/Kolkata')  
    gmt_time = gmt_time.replace(tzinfo=pytz.utc)  
    ist_time = gmt_time.astimezone(ist_timezone)  
    formatted_time = ist_time.strftime('%Y-%m-%d %I:%M:%S %p IST')  
    return formatted_time

def convert_grade_to_integer(grade):
    grade_mapping = {
        'O': 10, 'E': 9, 'A': 8, 'B': 7, 'C': 6, 'D': 5, 'S': 0, 'M': 0, 'F': 0
    }
    return grade_mapping.get(grade, 0)  

def calculate_sgpa(result):
    total_credits = 0
    total_weighted_grades = 0
    
    for row in result:
        credits_parts = [float(part) for part in row[7].split('+')]
        total_credits += sum(credits_parts)
        
        if set(row[8]) <= {'O', 'E', 'A', 'B', 'C', 'D', 'S', 'M', 'F'}:
            grade = convert_grade_to_integer(row[8])
        else:
            grade = float(row[8])
        
        weighted_grade = grade * sum(credits_parts)
        total_weighted_grades += weighted_grade
    
    sgpa = total_weighted_grades / total_credits if total_credits != 0 else 0  
    return sgpa, total_credits

def calculate_cgpa(registration, name):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT Credits, Grade FROM CUTM WHERE (Reg_No = ? OR LOWER(Name) = LOWER(?))", (registration, name))
    rows = cur.fetchall()
    conn.close()

    total_credits = 0
    total_weighted_grades = 0

    for row in rows:
        credits_parts = [float(part) for part in row[0].split('+')]
        
        if set(row[1]) <= {'O', 'E', 'A', 'B', 'C', 'D', 'S', 'M', 'F'}:
            grade = convert_grade_to_integer(row[1])
        else:
            grade = float(row[1])
        
        total_credits += sum(credits_parts)
        weighted_grade = grade * sum(credits_parts)
        total_weighted_grades += weighted_grade

    cgpa = total_weighted_grades / total_credits if total_credits != 0 else 0
    return cgpa

@app.route('/', methods=['GET', 'POST'])
def home():
    # Return simple HTML if templates don't exist
    if not os.path.exists('templates/index.html'):
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CUTM Result Portal</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                h1 { color: #4682b4; text-align: center; }
                .form-group { margin: 20px 0; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                button { background: #4682b4; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #36648b; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CUTM Result Portal</h1>
                <p style="text-align: center; color: #666;">University of Technology and Management, PKD</p>
                <form method="post">
                    <div class="form-group">
                        <label>Registration Number:</label>
                        <input type="number" name="registration" required>
                    </div>
                    <div class="form-group">
                        <label>Semester:</label>
                        <select name="semester" required>
                            <option value="">Select Semester</option>
                            <option value="1">Semester 1</option>
                            <option value="2">Semester 2</option>
                            <option value="3">Semester 3</option>
                            <option value="4">Semester 4</option>
                            <option value="5">Semester 5</option>
                            <option value="6">Semester 6</option>
                            <option value="7">Semester 7</option>
                            <option value="8">Semester 8</option>
                        </select>
                    </div>
                    <div style="text-align: center;">
                        <button type="submit">Search Results</button>
                    </div>
                </form>
                <p style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                    &copy; 2025 The New CUTM Result Portal 2.0. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        '''
    
    # Handle POST request
    if request.method == 'POST':
        registration = request.form.get('registration')
        semester = request.form.get('semester')
        
        try:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute("SELECT * FROM `CUTM` WHERE Reg_No = ? AND Sem = ?", (registration, semester))
            result = cur.fetchall()
            count = len(result)
            conn.close()
            
            return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Search Results</title></head>
            <body style="font-family: Arial, sans-serif; margin: 40px;">
                <h1>Search Results</h1>
                <p>Registration: {registration}</p>
                <p>Semester: {semester}</p>
                <p>Records found: {count}</p>
                {"<p style='color: red;'>No records found</p>" if count == 0 else "<p style='color: green;'>Records found!</p>"}
                <a href="/">Back to Search</a>
            </body>
            </html>
            '''
        except Exception as e:
            return f"<h1>Database Error</h1><p>{str(e)}</p><a href='/'>Back</a>"
    
    # Try to use template if it exists
    try:
        return render_template('index.html', semesters=[])
    except Exception as e:
        logger.error(f"Template error: {e}")
        return "<h1>CUTM Result Portal</h1><p>Service is running but templates are not available.</p>"

@app.route('/semesters', methods=['POST'])
def get_semesters():
    try:
        registration = request.form.get('registration')
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT Sem FROM `CUTM` WHERE Reg_No = ?", (registration,))
        semesters = [row[0] for row in cur.fetchall()]
        conn.close()
        return jsonify(semesters=semesters)
    except:
        return jsonify(error='Failed to fetch semesters')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    return redirect('/')

@app.route('/admin/panel')
def admin_panel():
    return redirect('/')

@app.route('/admin/logout')
def admin_logout():
    return redirect('/')

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'CUTM Result Portal is running'}

@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        return '''
        <html>
        <head><title>About - CUTM Result Portal</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>About CUTM Result Portal</h1>
            <p>The New CUTM Result Portal 2.0 provides easy access to student results.</p>
            <p>Developed by Yuvraj Sharma</p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        ''', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)