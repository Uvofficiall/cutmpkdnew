from flask import Flask, render_template, request, redirect, jsonify
import os
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
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
    # Add sample data if table is empty
    cur.execute("SELECT COUNT(*) FROM CUTM")
    if cur.fetchone()[0] == 0:
        sample_data = [
            ('245804120001', 'John Doe', '1', '4', 'A'),
            ('245804120002', 'Jane Smith', '1', '3', 'B'),
            ('245804120001', 'John Doe', '2', '4', 'O'),
        ]
        cur.executemany("INSERT INTO CUTM (Reg_No, Name, Sem, Credits, Grade) VALUES (?, ?, ?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        registration = request.form.get('registration')
        semester = request.form.get('semester')
        
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM CUTM WHERE Reg_No = ? AND Sem = ?", (registration, semester))
        results = cur.fetchall()
        conn.close()
        
        if results:
            result_html = "<h3>Results Found:</h3><ul>"
            for row in results:
                result_html += f"<li>Name: {row[2]}, Credits: {row[4]}, Grade: {row[5]}</li>"
            result_html += "</ul>"
        else:
            result_html = "<p style='color: red;'>No records found</p>"
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CUTM Result Portal</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #4682b4, #36648b); color: white; }}
                .container {{ max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 15px; backdrop-filter: blur(10px); }}
                h1 {{ text-align: center; margin-bottom: 30px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
                .form-group {{ margin: 20px 0; }}
                label {{ display: block; margin-bottom: 8px; font-weight: bold; }}
                input, select {{ width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 16px; }}
                button {{ background: #003366; color: white; padding: 15px 40px; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; margin: 10px 5px; }}
                button:hover {{ background: #002244; transform: scale(1.05); }}
                .results {{ background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin-top: 20px; }}
                a {{ color: #e9ecef; text-decoration: none; }}
                a:hover {{ color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎓 CUTM Result Portal 2.0</h1>
                <p style="text-align: center; margin-bottom: 30px;">University of Technology and Management, PKD</p>
                
                <div class="results">
                    {result_html}
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/"><button>🔍 New Search</button></a>
                    <a href="/about"><button>ℹ️ About</button></a>
                </div>
                
                <p style="text-align: center; margin-top: 40px; font-size: 12px; opacity: 0.8;">
                    © 2025 The New CUTM Result Portal 2.0. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        '''
    
    # GET request - show form
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Sem FROM CUTM ORDER BY Sem")
    semesters = [row[0] for row in cur.fetchall()]
    conn.close()
    
    semester_options = ""
    for sem in semesters:
        semester_options += f'<option value="{sem}">Semester {sem}</option>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CUTM Result Portal</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #4682b4, #36648b); color: white; min-height: 100vh; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
            .card {{ background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
            h1 {{ text-align: center; margin-bottom: 10px; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
            .subtitle {{ text-align: center; margin-bottom: 40px; opacity: 0.9; }}
            .form-group {{ margin: 25px 0; }}
            label {{ display: block; margin-bottom: 8px; font-weight: bold; font-size: 16px; }}
            input, select {{ width: 100%; padding: 15px; border: none; border-radius: 10px; font-size: 16px; box-sizing: border-box; }}
            input:focus, select:focus {{ outline: none; box-shadow: 0 0 10px rgba(255,255,255,0.5); }}
            .btn {{ background: #003366; color: white; padding: 18px 50px; border: none; border-radius: 30px; cursor: pointer; font-size: 18px; width: 100%; margin-top: 20px; transition: all 0.3s; }}
            .btn:hover {{ background: #002244; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
            .nav {{ text-align: center; margin-top: 30px; }}
            .nav a {{ color: #e9ecef; text-decoration: none; margin: 0 15px; }}
            .nav a:hover {{ color: white; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 12px; opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>🎓 Centurion</h1>
                <p class="subtitle">University of Technology and Management, PKD<br>Result Portal 2.0</p>
                
                <form method="post">
                    <div class="form-group">
                        <label>📝 Registration Number:</label>
                        <input type="text" name="registration" placeholder="Enter your registration number" required>
                    </div>
                    
                    <div class="form-group">
                        <label>📚 Semester:</label>
                        <select name="semester" required>
                            <option value="">Select Semester</option>
                            {semester_options}
                        </select>
                    </div>
                    
                    <button type="submit" class="btn">🔍 Search Results</button>
                </form>
                
                <div class="nav">
                    <a href="/about">ℹ️ About</a>
                    <a href="/health">💚 Status</a>
                </div>
                
                <div class="footer">
                    © 2025 The New CUTM Result Portal 2.0. All rights reserved.<br>
                    Developed by Yuvraj Sharma
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - CUTM Result Portal</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #4682b4, #36648b); color: white; min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
            .card { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); }
            h1 { text-align: center; margin-bottom: 30px; }
            p { line-height: 1.6; margin-bottom: 20px; }
            .btn { background: #003366; color: white; padding: 12px 30px; border: none; border-radius: 25px; text-decoration: none; display: inline-block; margin-top: 20px; }
            .btn:hover { background: #002244; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>About CUTM Result Portal 2.0</h1>
                <p><strong>The New CUTM Result Portal 2.0</strong> provides fast, secure, and convenient access to student academic results.</p>
                <p><strong>Developer:</strong> Yuvraj Sharma<br>
                B.Tech CSE Student (2023-2027)<br>
                Centurion University of Technology and Management, Paralakhemundi, Odisha</p>
                <p>This portal was built with a clear vision: to provide students with easy access to their academic results with a minimalist design that prioritizes performance and functionality.</p>
                <a href="/" class="btn">🏠 Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'CUTM Result Portal is running', 'database': 'connected'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)