from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()  # Laad de omgevingsvariabelen uit .env

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Haal de secret key op uit omgevingsvariabelen
app.config['UPLOAD_FOLDER'] = 'uploads'

# Haal de gebruikersgegevens op uit omgevingsvariabelen
USERNAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Debug output
        print(f"Provided username: {username}")
        print(f"Provided password: {password}")
        print(f"Expected username: {USERNAME}")
        print(f"Expected password: {PASSWORD}")
        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('index'))
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
def generate():
    if 'user' not in session:
        return redirect(url_for('login'))
    faqs = request.json.get('faqs', [])
    code = generate_faq_code(faqs)
    return jsonify({'code': code})

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        faqs = process_csv(filepath)
        return jsonify({'faqs': faqs})
    return "Invalid file"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def process_csv(filepath):
    df = pd.read_csv(filepath)
    # Controleer en verwijder eventuele voor- en achterliggende spaties in de kolomnamen
    df.columns = [col.strip() for col in df.columns]
    
    # Verwijder aanhalingstekens en extra spaties rondom de waarden
    df['Antwoord'] = df['Antwoord'].str.replace('"', '').str.strip()
    df['Vraag'] = df['Vraag'].str.replace('"', '').str.strip()

    # Debug output om te controleren of de kolommen correct zijn gelezen
    # print(df.head())

    # Hernoem de kolommen naar Engels zoals de frontend verwacht
    df = df.rename(columns={'Vraag': 'question', 'Antwoord': 'answer'})
    faqs = df.to_dict(orient='records')

    # print(faqs)
    return faqs

def generate_faq_code(faqs):
    # Stijl en HTML voor de gegenereerde code
    style = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Roboto', sans-serif;
        }
        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #424242;
        }
        .container {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .faq-title {
            display: flex;
            justify-content: center;
            font-size: 2rem;
            font-weight: bold;
        }
        .accordeon {
            background-color: #fff;
            border-radius: 8px;
            padding: 12px;
            cursor: pointer;
            box-shadow: 5px 5px 5px rgba(0, 0, 0, 0.1);
        }
        .accordeon-header {
            border: none;
            width: 100%;
            display: flex;
            justify-content: left;
            gap: 1rem;
            align-items: center;
            background-color: transparent;
            font-size: 1.25rem;
            font-weight: bold;
            cursor: pointer;
            padding: 8px;
        }
        .accordeon-header span {
            max-width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .accordeon-body {
            color: #444;
            text-align: left;
            font-size: 1.15rem;
            opacity: 0;
            height: 0;
            overflow: hidden;
            transition: opacity .3s;
        }
        .accordeon-body.active {
            height: auto;
            opacity: 1;
            padding: 5px;
        }
        .arrow {
            transition: transform .2s linear;
        }
        .accordeon.open .arrow {
            transform: rotate(180deg);
        }
    </style>
    """

    html = f"{style}<div class='container'><h2 class='faq-title'>Veelgestelde Vragen</h2>"

    for faq in faqs:
        html += f"""
        <div class='accordeon'>
            <button class='accordeon-header'>
                <svg class='arrow' viewBox='0 0 320 512' width='16' title='angle-down'>
                    <path d='M143 352.3L7 216.3c-9.4-9.4-9.4-24.6 0-33.9l22.6-22.6c9.4-9.4 24.6-9.4 33.9 0l96.4 96.4 96.4-96.4c9.4-9.4 24.6-9.4 33.9 0l22.6 22.6c9.4 9.4 9.4 24.6 0 33.9l-136 136c-9.2 9.4-24.4 9.4-33.8 0z'/>
                </svg>
                <span>{faq['Vraag']}</span>
            </button>
            <div class='accordeon-body'>
                <p>{faq['Amtwoord']}</p>
            </div>
        </div>
        """

    html += """
    </div>
    <script>
        document.querySelectorAll('.accordeon-header').forEach(button => {
            button.addEventListener('click', () => {
                const accordeonBody = button.nextElementSibling;
                const accordeon = button.parentElement;
                
                if (accordeonBody.classList.contains('active')) {
                    accordeonBody.classList.remove('active');
                    accordeon.classList.remove('open');
                } else {
                    document.querySelectorAll('.accordeon-body.active').forEach(activeBody => {
                        activeBody.classList.remove('active');
                        activeBody.parentElement.classList.remove('open');
                    });
                    accordeonBody.classList.add('active');
                    accordeon.classList.add('open');
                }
            });
        });
    </script>
    """

    return html

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
