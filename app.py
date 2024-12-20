from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from functools import wraps

load_dotenv()  # Laad de omgevingsvariabelen uit .env

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Haal de secret key op uit omgevingsvariabelen
app.config['UPLOAD_FOLDER'] = 'uploads'

# Haal de gebruikersgegevens op uit omgevingsvariabelen
USERNAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')

LOGIN_REQUIRED = os.getenv('LOGIN_REQUIRED', 'False').lower() == 'true'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if LOGIN_REQUIRED and 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

print(USERNAME)
print(PASSWORD)
print('FLASK_SECRET_KEY', app.secret_key)

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('home'))
        return "Invalid credentials"
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/faq-generator')
@login_required
def faq_generator():
    return render_template('faq_generator.html')

@app.route('/pricing-table-generator')
@login_required
def pricing_table_generator():
    return render_template('pricing_table_generator.html')

@app.route('/generate', methods=['POST'])
@login_required
def generate_faq_code():
    faqs = request.json.get('faqs', [])
    code = generate_faq_code(faqs)
    return jsonify({'code': code})

@app.route('/upload_csv', methods=['POST'])
@login_required
def upload_csv():
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

@app.route('/generate_pricing_table', methods=['POST'])
@login_required
def generate_pricing_table():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        pricing_html = generate_pricing_html(data)
        return jsonify({'code': pricing_html})
    except Exception as e:
        # Print de foutmelding naar de server-log voor debugging
        print(f"Error in generate_pricing_table: {e}")
        # Retourneer een JSON-response met de foutmelding
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def process_csv(filepath):
    df = pd.read_csv(filepath)
    # Controleer en verwijder eventuele voor- en achterliggende spaties in de kolomnamen
    df.columns = [col.strip() for col in df.columns]
    
    # Verwijder aanhalingstekens en extra spaties rondom de waarden
    df['Antwoord'] = df['Antwoord'].str.replace('"', '').str.strip()
    df['Vraag'] = df['Vraag'].str.replace('"', '').str.strip()

    # Hernoem de kolommen naar Engels zoals de frontend verwacht
    df = df.rename(columns={'Vraag': 'question', 'Antwoord': 'answer'})
    faqs = df.to_dict(orient='records')
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
                <span>{faq['question']}</span>
            </button>
            <div class='accordeon-body'>
                <p>{faq['answer']}</p>
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

def generate_pricing_html(data):
    height_per_function_line = 80
    total_height = 600
    image_height = 120

    # Bepaal de minimale hoogte van de tabel op basis van het aantal features
    for plan in data["plans"]:
        new_height = len(plan.get("features", [])) * height_per_function_line + image_height
        if new_height > total_height:
            total_height = new_height

    # Begin van de HTML-opbouw
    html = """
    <div class="wrap">
        <div class="miswitch">
            <div class="switch-btn" id="switch-btn"></div>
            <a id="quarter-btn">Kwartaal</a>
            <a id="year-btn">Jaar</a>
        </div>
        <div class="pricing-wrap">
    """

    # Genereer HTML voor elk plan
    for plan in data['plans']:
        name = plan.get('name', 'N/A')
        quarterly_price = plan.get('quarterly_price', '0')
        yearly_price = plan.get('yearly_price', '0')
        full_yearly_price = plan.get('full_yearly_price', '0')
        features = plan.get('features', [])
        yearly_url = plan.get('yearly_url', '#')
        quarterly_url = plan.get('quarterly_url', '#')
        image_url = plan.get('image_url')

        html += f"""
        <div class="pricing-table">
            <div class="pricing-table-cont">
                <div class="pricing-table-quarter">
                    <div class="pricing-table-head">
        """

        # Voeg image_url toe als deze bestaat
        if image_url:
            html += f"""
            <div class="image-container">
                <img src="{image_url}" alt="Afbeelding voor {name}">
            </div>
            """

        html += f"""
                        <h2>{name}</h2>
                        <h3><sup>€</sup>{quarterly_price}<sub>/kwartaal</sub></h3>
                    </div>
                    <ul class="pricing-table-list">
        """

        # Voeg elke feature toe aan de lijst
        for feature in features:
            html += f"<li>{feature}</li>"
        
        html += f"""
                    </ul>
                    <a href="{quarterly_url}" class="pricing-table-button" target="_blank">Kies dit plan</a>
                </div>
                <div class="pricing-table-year">
                    <div class="pricing-table-head">
        """

        # Voeg image_url toe voor het jaarplan als het beschikbaar is
        if image_url:
            html += f"""
            <div class="image-container">
                <img src="{image_url}" alt="Afbeelding voor {name}">
            </div>
            """

        html += f"""
                        <h2>{name}</h2>
                        <h3><sup>€</sup>{yearly_price}<sub>/jaar</sub></h3>
                        <h4><del>€{full_yearly_price}</del></h4>
                    </div>
                    <ul class="pricing-table-list">
        """

        for feature in features:
            html += f"<li>{feature}</li>"
        
        html += f"""
                    </ul>
                    <a href="{yearly_url}" class="pricing-table-button" target="_blank">Kies dit plan</a>
                </div>
            </div>
        </div>
        """

    # Sluit de HTML en voeg CSS en JavaScript toe
    html += f"""
        </div>
    </div>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Open sans', sans-serif;
        }}
        a {{
            text-decoration: none;
        }}
        ul {{
            list-style: none;
        }}
        .wrap {{
            width: 90%;
            max-width: 1170px;
            margin: 50px auto;
        }}
        .miswitch {{
            /* border: 1px solid #121212; */
            border-radius: 20px;
            color: #fff;
            position: relative;
            margin: 0px auto 50px;
            width: 200px;
            overflow: hidden;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            background-color: #000;
        }}
        .miswitch a {{
            font-size: 14px;
            z-index: 2;
            position: relative;
            width: 50%;
            text-align: center;
            cursor: pointer;
        }}
        .switch-btn {{
            position: absolute;
            background: #990000;
            width: 50%;
            height: 90%;
            border-radius: 20px;
            top: 2px;
            left: 2px;
            z-index: 1;
            transition: all .5s;
        }}
        .on {{
            left: 97px;
        }}
        /* Prijstabelstijl */
        .pricing-table .image-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        .pricing-table .image-container img {{
            width: 70%;
            height: auto;
            object-fit: contain; /* Houd de verhoudingen */
        }}
        .pricing-wrap {{
            width: 100%;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }}
        .pricing-table {{
            width: 32%;
            transition: transform .5s ease;
            perspective: 2000px;
        }}
        .pricing-table:hover {{
            transform: scale(1.07);
        }}
        .pricing-table-cont {{
            text-align: center;
            position: relative;
            /* min-height: {total_height}px; */
            min-height: 1000px;
            transform-style: preserve-3d;
            transition: .3s ease;
        }}
        .pricing-table-quarter,
        .pricing-table-year {{
            backface-visibility: hidden;
            position: absolute;
            width: 100%;
            top: 0;
            left: 0;
            background: #fff;
            border-radius: 50px;
        }}
        .pricing-table-year {{
            transform: rotateY(180deg);
        }}
        .rotation-table {{
            transform: rotateY(180deg);
        }}
        .pricing-table-head {{
            color: #121212;
            padding: 30px 0px;
        }}
        .pricing-table-head h2 {{
            font-size: 16px;
            letter-spacing: 2px;
            font-weight: bold;
        }}
        .pricing-table-head h3 {{
            font-size: 60px;
            font-weight: 400;
            display: inline;
        }}
        .pricing-table-head h4 {{
            font-size: 30px;
            font-weight: 400;
        }}
        .pricing-table-head h3 sup,
        .pricing-table-head h3 sub {{
            font-size: 20px;
            color: #ABB8C0;
            font-weight: 600;
        }}
        .pricing-table-list li {{
            background: #F1F3F5;
            padding: 15px;
        }}
        .pricing-table-list li:nth-child(2n) {{
            background: #fff;
        }}
        .pricing-table-button {{
            display: block;
            border-radius: 2rem;
            width: 100%;
            padding: 20px 0;
            background: #121212;
            color: #fff;
            margin-top: 23px;
        }}
        .pricing-table-button:hover {{
            background-color: #990000;
        }}

        /* Responsive styling */
        @media screen and (max-width: 750px) {{
        .miswitch {{
          display: none;
        }}

        .pricing-wrap {{
            flex-direction: column;
            align-items: center;
        }}

        .pricing-table {{
            width: 100%;
            margin-bottom: 0px;
            perspective: none; /* Flip-effect verwijderen op mobiel */
        }}

        .pricing-table-cont {{
            position: static; /* Stop overlapping */
            transform: none; /* Geen rotatie op mobiel */
        }}

        .pricing-table-quarter,
        .pricing-table-year {{
            position: relative; /* Herstel normale flow */
            transform: none;
            backface-visibility: visible; /* Zorg dat beide kanten zichtbaar zijn */
            margin-bottom: 20px;
        }}

        .pricing-table-list {{
          display: none;
        }}
    }}

    @media screen and (max-width: 500px) {{
        .pricing-table {{
            width: 100%;
            margin-bottom: 15px;
        }}
    }}
    </style>
    <script>
        document.querySelectorAll('.miswitch a').forEach(function(anchor) {{
            anchor.addEventListener('click', function() {{
                let switchBtn = document.querySelector('.switch-btn')
                switchBtn.classList.toggle('on')
                document.querySelectorAll('.pricing-table-cont').forEach(function(cont) {{
                    cont.classList.toggle('rotation-table')
                }})
            }})
        }})
    </script>
    """

    return html

@app.route('/upload_pricing_csv', methods=['POST'])
@login_required
def upload_pricing_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        plans = process_pricing_csv(filepath)
        return jsonify({'plans': plans})
    return jsonify({'error': 'Invalid file'}), 400

def process_pricing_csv(filepath):
    df = pd.read_csv(filepath)
    df.columns = [col.strip() for col in df.columns]

    # Zorg ervoor dat de functies worden opgesplitst als puntkomma-gescheiden lijst
    plans = df.to_dict(orient='records')
    for plan in plans:
        if isinstance(plan['features'], str):
            plan['features'] = [feature.strip() for feature in plan['features'].split(';')]
        if 'image_url' not in plan:
            plan['image_url'] = ''  # Zorg ervoor dat er een lege waarde is als 'image_url' ontbreekt

    return plans

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
