from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    faqs = request.json.get('faqs', [])
    code = generate_faq_code(faqs)
    return jsonify({'code': code})

def generate_faq_code(faqs):
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

if __name__ == '__main__':
    app.run(debug=True)
