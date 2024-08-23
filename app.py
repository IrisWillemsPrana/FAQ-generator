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

# print(USERNAME)
# print(PASSWORD)

@app.route('/')
def home():
    if 'user' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        session['user'] = username

        return redirect(url_for('home'))
        # if username == USERNAME and password == PASSWORD:
        #     session['user'] = username
        #     return redirect(url_for('home'))
        # return "Invalid credentials"
    return render_template('login.html')
    

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/faq-generator')
def faq_generator():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('faq_generator.html')

@app.route('/pricing-table-generator')
def pricing_table_generator():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('pricing_table_generator.html')

@app.route('/generate', methods=['POST'])
def generate_faq_code():
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

@app.route('/generate_pricing_table', methods=['POST'])
def generate_pricing_table():
    if 'user' not in session:
        return redirect(url_for('login'))
    data = request.json
    pricing_html = generate_pricing_html(data)
    return jsonify({'code': pricing_html})

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
    # set minimum total height
    total_height = 500 

    for plan in data["plans"]:
        # print(len(plan["features"]))
        new_height = len(plan["features"]) * height_per_function_line
        if new_height > total_height:
            total_height = new_height
            print(total_height)

    html = """
    <div class="wrap">
        <div class="miswitch">
            <div class="switch-btn" id="switch-btn"></div>
            <a id="quarter-btn">Kwartaal</a>
            <a id="year-btn">Jaar</a>
        </div>
        <div class="pricing-wrap">
    """

    for plan in data['plans']:
        html += f"""
        <div class="pricing-table">
            <div class="pricing-table-cont">
                <div class="pricing-table-quarter">
                    <div class="pricing-table-head">
                        <h2>{plan['name']}</h2>
                        <h3><sup>€</sup>{plan['quarterly_price']}<sub>/kwartaal</sub></h3>
                    </div>
                    <ul class="pricing-table-list">
        """
        for feature in plan['features']:
            html += f"<li>{feature}</li>"

        html += f"""
                    </ul>
                    <a href="{plan['url']}" class="pricing-table-button">Kies dit plan</a>
                </div>
                <div class="pricing-table-year">
                    <div class="pricing-table-head">
                        <h2>{plan['name']}</h2>
                        <h3><sup>€</sup>{plan['yearly_price']}<sub>/jaar</sub></h3>
                        <h4><del>€{plan['full_yearly_price']}</del></h4>
                    </div>
                    <ul class="pricing-table-list">
        """
        for feature in plan['features']:
            html += f"<li>{feature}</li>"

        html += f"""
                    </ul>
                    <a href="{plan['url']}" class="pricing-table-button">Kies dit plan</a>
                </div>
            </div>
        </div>
        """

    html += """
        </div>
    </div>
    <style>
        * {
            margin: 0;
            padding: 0;
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            box-sizing: border-box;
        }

        body {
            font-family: 'Open sans', sans-serif;
        }

        a {
            text-decoration: none;
        }

        ul {
            list-style: none;
        }

        .wrap {
            width: 90%;
            max-width: 1170px;
            margin: 50px auto;
        }

        .miswitch {
            border: 1px solid #121212;
            border-radius: 20px;
            color: #fff;
            position: relative;
            margin: 0px auto 50px;
            width: 200px;
            overflow: hidden;
            padding: 10px;
            display: flex;
            justify-content: space-between;
        }

        .miswitch a {
            font-size: 14px;
            z-index: 2;
            position: relative;
            width: 50%;
            text-align: center;
            cursor: pointer;
        }

        .switch-btn {
            position: absolute;
            background: #0C1F28;
            width: 50%;
            height: 90%;
            border-radius: 20px;
            top: 2px;
            left: 2px;
            z-index: 1;
            transition: all .5s;
        }

        .on {
            left: 97px;
        }

        /* Price Table */
        .pricing-wrap {
            width: 100%;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }

        .pricing-table {
            width: 32%;
            transition: transform .5s ease;
            -webkit-perspective: 2000px;
            perspective: 2000px;
        }

        .pricing-table:hover {
            transform: scale(1.07);
        }

        .pricing-table-cont {
            background: #fff;
            text-align: center;
            position: relative;"""

    html += f"""
            min-height: {total_height}px;"""
            
    html += """
            -webkit-transform-style: preserve-3d;
            transform-style: preserve-3d;
            transition: .3s ease;
        }

        .pricing-table-quarter,
        .pricing-table-year {
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            position: absolute;
            width: 100%;
            top: 0;
            left: 0;
            background: #fff;
        }

        .pricing-table-year {
            transform: rotateY(180deg);
        }

        .rotation-table {
            transform: rotateY(180deg);
        }

        .pricing-table-head {
            color: #121212;
            padding: 30px 0px;
        }

        .pricing-table-head h2 {
            font-size: 16px;
            letter-spacing: 2px;
            font-weight: bold;
        }

        .pricing-table-head h3 {
            font-size: 60px;
            font-weight: 400;
            display: inline;
        }

        .pricing-table-head h4 {
            font-size: 30px;
            font-weight: 400;
        }

        .pricing-table-head h3 sup,
        .pricing-table-head h3 sub {
            font-size: 20px;
            color: #ABB8C0;
            font-weight: 600;
        }

        .pricing-table-head h3 sub {
            font-size: 13px;
        }

        .pricing-table-head.silver-title h2,
        .pricing-table-head.silver-title h3,
        .pricing-table-head.silver-title h3 sup,
        .pricing-table-head.silver-title h3 sub {
            color: #298039;
        }

        .pricing-table-list li {
            background: #F1F3F5;
            padding: 10px 0;
        }

        .pricing-table-list li:nth-child(2n) {
            background: #fff;
        }

        .pricing-table-button {
            display: block;
            border-radius: 2rem;
            width: 100%;
            padding: 20px 0;
            background: #121212;
            color: #fff;
            margin-top: 23px;
        }

        .pricing-table-button.silver {
            background: #298039;
        }

        /* RESPONSIVE ===============================  */
        @media screen and (max-width: 750px) {
            .pricing-table {
                width: 72%;
                margin-bottom: 20px;
            }

            .pricing-wrap {
                justify-content: center;
            }

            .pricing-table:hover {
                transform: scale(1.0);
            }
        }

        @media screen and (max-width: 500px) {
            .pricing-table {
                width: 90%;
            }
        }
    </style>
    <script>
        // Listen for clicks on the anchor tags within the .miswitch class
        document.querySelectorAll('.miswitch a').forEach(function(anchor) {
            anchor.addEventListener('click', function() {
                // Toggle the 'on' class on the switch button
                let switchBtn = document.querySelector('.switch-btn')
                switchBtn.classList.toggle('on')

                // Toggle the 'rotation-table' class on all pricing table containers
                document.querySelectorAll('.pricing-table-cont').forEach(function(cont) {
                    cont.classList.toggle('rotation-table')
                })
            })
        })
    </script>
    """

    return html

@app.route('/upload_pricing_csv', methods=['POST'])
def upload_pricing_csv():
    if 'user' not in session:
        return jsonify({'error': 'Not authorized'}), 401
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
    
    plans = df.to_dict(orient='records')

    # Gebruik een puntkomma (;) als scheidingsteken voor de functies
    for plan in plans:
        if isinstance(plan['features'], str):
            plan['features'] = [feature.strip() for feature in plan['features'].split(';')]
    
    return plans

# def generate_pricing_html(data):
#     html = """
#     <div class="wrap">
#         <div class="miswitch">
#             <div class="switch-btn" id="switch-btn"></div>
#             <a id="month-btn">Maand</a>
#             <a id="year-btn">Jaar</a>
#         </div>
#         <div class="pricing-wrap">
#     """

#     for plan in data['plans']:
#         html += f"""
#         <div class="pricing-table">
#             <div class="pricing-table-cont">
#                 <div class="pricing-table-month">
#                     <div class="pricing-table-head">
#                         <h2>{plan['name']} MAAND</h2>
#                         <h3><sup>€</sup>{plan['monthly_price']}<sub>/maand</sub></h3>
#                     </div>
#                     <ul class="pricing-table-list">
#         """
#         for feature in plan['features']:
#             html += f"<li><span> {plan['name']} </span>{feature}</li>"

#         html += f"""
#                     </ul>
#                     <a href="#" class="pricing-table-button">Kies dit plan</a>
#                 </div>
#                 <div class="pricing-table-year">
#                     <div class="pricing-table-head">
#                         <h2>{plan['name']} JAAR</h2>
#                         <h3><sup>€</sup>{plan['yearly_price']}<sub>/jaar</sub></h3>
#                         <h4><del>{plan['yearly_discount_price']}</del></h4>
#                     </div>
#                     <ul class="pricing-table-list">
#         """
#         for feature in plan['features']:
#             html += f"<li><span> {plan['name']} </span>{feature}</li>"

#         html += f"""
#                     </ul>
#                     <a href="#" class="pricing-table-button">Kies dit plan</a>
#                 </div>
#             </div>
#         </div>
#         """

#     html += """
#         </div>
#     </div>
#     <style>
#         *{
# 			margin: 0;
# 			padding: 0;
# 			-webkit-box-sizing: border-box;
# 			-moz-box-sizing: border-box;
# 			box-sizing: border-box;
# 			}

# 		body{
# 			font-family: 'Open sans', sans-serif;
# 			}

# 		a{
# 			text-decoration: none;
# 			}

# 		ul{
# 			list-style: none;
# 			}

# 		.wrap{
# 			width: 90%;
# 			max-width: 1170px;
# 			margin: 50px auto;
# 			}

# 		.miswitch{
# 			border: 1px solid #121212;
# 			border-radius: 20px;
# 			color: #fff;
# 			position: relative;
# 			margin: 0px auto 50px;
# 			width: 200px;
# 			overflow: hidden;
# 			padding: 10px;
# 			display: flex;
# 			justify-content: space-between;
# 			}

# 		.miswitch a{
# 			font-size: 14px;
# 			z-index: 2;
# 			position: relative;
# 			width: 50%;
# 			text-align: center;
# 			cursor: pointer;
# 			}

# 		.switch-btn{
# 			position: absolute;
# 			background: #0C1F28;
# 			width: 50%;
# 			height: 90%;
# 			border-radius: 20px;
# 			top: 2px;
# 			left: 2px;
# 			z-index: 1;
# 			transition: all .5s;
# 			}

# 		.on{
# 			left: 97px;
# 			}

# 		/* Price Table */
# 		.pricing-wrap{
# 			width: 100%;
# 			display: flex;
# 			justify-content: space-between;
# 			flex-wrap: wrap;
# 		}

# 		.pricing-table{
# 			width: 32%;
# 			transition: transform .5s ease;

# 			-webkit-perspective: 2000px;
# 			perspective: 2000px;
# 		}

# 		.pricing-table:hover{
# 			transform: scale(1.07);
# 		}

# 		.pricing-table-cont{
# 			background: #fff;
# 			text-align: center;
# 			position: relative;
# 			height: 500px;

# 			-webkit-transform-style: preserve-3d;
# 			transform-style: preserve-3d;

# 			transition: .3s ease;
# 		}

# 		.pricing-table-month, .pricing-table-year{
# 			-webkit-backface-visibility: hidden;
# 			backface-visibility: hidden;
# 			position: absolute;
# 			width: 100%;
# 			height: 100%;
# 			top: 0;
# 			left: 0;
# 			background: #fff;
# 		}

# 		.pricing-table-quarter{
# 			transform: rotateY(180deg);
# 		}

# 		.pricing-table-year{
# 			transform: rotateY(180deg);
# 		}

# 		.rotation-table{
# 			transform: rotateY(180deg);
# 		}

# 		.pricing-table-head{
# 			color: #121212;
# 			padding: 30px 0px;
# 		}

# 		.pricing-table-head h2{
# 			font-size: 16px;
# 			letter-spacing: 2px;	
# 			font-weight: bold;
# 		}

# 		.pricing-table-head h3{
# 			font-size: 60px;
# 			font-weight: 400;
# 			display: inline;
# 		}

# 		.pricing-table-head h4{
# 			font-size: 30px;
# 			font-weight: 400;
# 		}

# 		.pricing-table-head h3 sup, .pricing-table-head h3 sub{
# 			font-size: 20px;
# 			color: #ABB8C0;
# 			font-weight: 600;
# 		}

# 		.pricing-table-head h3 sub{
# 			font-size: 13px;
# 		}

# 		.pricing-table-head.silver-title h2,
# 		.pricing-table-head.silver-title h3,
# 		.pricing-table-head.silver-title h3 sup,
# 		.pricing-table-head.silver-title h3 sub{
# 			color: #298039;
# 		}

# 		.pricing-table-list li{
# 			background: #F1F3F5;
# 			padding: 10px 0;
# 		}

# 		.pricing-table-list li:nth-child(2n){
# 			background: #fff;
# 		}

# 		.pricing-table-button{
# 			display: block;
# 			border-radius: 2rem;
# 			width: 100%;
# 			padding: 20px 0;
# 			background: #121212;
# 			color: #fff;
# 			margin-top: 23px;
# 		}

# 		.pricing-table-button.silver{
# 			background: #298039;
# 		}

# 		/* RESPONSIVE ===============================  */
# 		@media screen and (max-width: 750px){
# 			.pricing-table{
# 				width: 72%;
# 				margin-bottom: 20px;
# 			}

# 			.pricing-wrap{
# 				justify-content: center;
# 			}

# 			.pricing-table:hover{
# 				transform: scale(1.0) ;
# 			}
# 		}

# 		@media screen and (max-width: 500px){
# 			.pricing-table{
# 				width: 90%;
# 			}
# 		}
#     </style>
#     <script>
#         // Listen for clicks on the anchor tags within the .miswitch class
#         document.querySelectorAll('.miswitch a').forEach(function(anchor) {
#             anchor.addEventListener('click', function() {
#                 // Toggle the 'on' class on the switch button
#                 let switchBtn = document.querySelector('.switch-btn')
#                 switchBtn.classList.toggle('on')

#                 // Toggle the 'rotation-table' class on all pricing table containers
#                 document.querySelectorAll('.pricing-table-cont').forEach(function(cont) {
#                     cont.classList.toggle('rotation-table')
#                 })
#             })
#         })
#     </script>
#     """

#     return html

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
