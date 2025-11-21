#!/usr/bin/env python3
"""
Simple Web Interface for LawBrain
Access at: http://localhost:8080
"""

from flask import Flask, request, jsonify, render_template_string
from agent import app as lawbrain_app

flask_app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🧠 LawBrain - AI Law Firm</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .lawyers {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .lawyer {
            background: #f0f4ff;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            resize: vertical;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
            margin-top: 15px;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .response {
            margin-top: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            display: none;
        }
        .response.show {
            display: block;
        }
        .message {
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #28a745;
        }
        .message.user {
            border-left-color: #007bff;
        }
        .message strong {
            color: #667eea;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-size: 18px;
            display: none;
        }
        .loading.show {
            display: block;
        }
        .example {
            background: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            cursor: pointer;
            border: 1px solid #ffc107;
        }
        .example:hover {
            background: #ffe69c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 LawBrain - AI Law Firm</h1>
        <p class="subtitle">Your Full-Service AI Law Firm with 9 Specialized Lawyers</p>

        <div class="lawyers">
            <div class="lawyer">⚖️ Criminal Lawyer</div>
            <div class="lawyer">📋 Civil Litigation</div>
            <div class="lawyer">💼 Corporate Lawyer</div>
            <div class="lawyer">💡 IP Lawyer</div>
            <div class="lawyer">👨‍👩‍👧‍👦 Family Lawyer</div>
            <div class="lawyer">🏠 Real Estate</div>
            <div class="lawyer">👔 Employment Lawyer</div>
            <div class="lawyer">📜 Estate Planning</div>
            <div class="lawyer">🌍 Immigration Lawyer</div>
        </div>

        <h3>Example Questions (Click to use):</h3>
        <div class="example" onclick="setQuestion('I was arrested for DUI. What should I do?')">
            🚗 I was arrested for DUI. What should I do?
        </div>
        <div class="example" onclick="setQuestion('I want to start an LLC for my tech startup.')">
            💼 I want to start an LLC for my tech startup.
        </div>
        <div class="example" onclick="setQuestion('I need help with a divorce.')">
            👨‍👩‍👧‍👦 I need help with a divorce.
        </div>

        <h3>Ask Your Legal Question:</h3>
        <textarea id="question" placeholder="Type your legal question here..."></textarea>
        <button onclick="askLawyer()">Ask LawBrain</button>

        <div class="loading" id="loading">⚖️ Consulting with our specialist lawyers...</div>

        <div class="response" id="response"></div>
    </div>

    <script>
        function setQuestion(q) {
            document.getElementById('question').value = q;
        }

        async function askLawyer() {
            const question = document.getElementById('question').value;
            if (!question.trim()) {
                alert('Please enter a question');
                return;
            }

            const btn = document.querySelector('button');
            const loading = document.getElementById('loading');
            const response = document.getElementById('response');

            btn.disabled = true;
            loading.classList.add('show');
            response.classList.remove('show');
            response.innerHTML = '';

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });

                const data = await res.json();

                if (data.error) {
                    response.innerHTML = `<div class="message" style="border-left-color: red;">
                        <strong>Error:</strong> ${data.error}
                    </div>`;
                } else {
                    let html = '<h3>📋 LawBrain Response:</h3>';
                    data.messages.forEach(msg => {
                        const isUser = msg.type === 'user';
                        const name = msg.name || 'You';
                        const cssClass = isUser ? 'user' : '';
                        html += `<div class="message ${cssClass}">
                            <strong>${name}:</strong><br>
                            ${msg.content.replace(/\\n/g, '<br>')}
                        </div>`;
                    });
                    response.innerHTML = html;
                }

                response.classList.add('show');
            } catch (error) {
                response.innerHTML = `<div class="message" style="border-left-color: red;">
                    <strong>Error:</strong> ${error.message}
                </div>`;
                response.classList.add('show');
            } finally {
                btn.disabled = false;
                loading.classList.remove('show');
            }
        }
    </script>
</body>
</html>
"""

@flask_app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@flask_app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        # Invoke LawBrain
        result = lawbrain_app.invoke({
            'messages': [('user', question)]
        })

        # Format messages
        messages = []
        for msg in result.get('messages', []):
            if hasattr(msg, 'content'):
                messages.append({
                    'type': msg.__class__.__name__.lower(),
                    'name': getattr(msg, 'name', None),
                    'content': msg.content
                })

        return jsonify({'messages': messages})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\\n" + "="*60)
    print("🧠 LawBrain Web Interface Starting...")
    print("="*60)
    print("\\n📍 Access at: http://localhost:8080")
    print("\\n🔒 Press CTRL+C to stop\\n")
    flask_app.run(host='0.0.0.0', port=8080, debug=False)
