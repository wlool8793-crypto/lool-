#!/usr/bin/env python3
"""
Enhanced Web Interface for LawBrain with Graph Visualization
Mimics LangGraph Studio features in the browser
"""

from flask import Flask, request, jsonify, render_template_string
from agent import app as lawbrain_app
import json

flask_app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🧠 LawBrain Studio - Enhanced Interface</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            height: 100vh;
            overflow: hidden;
        }

        .app-container {
            display: grid;
            grid-template-columns: 350px 1fr;
            height: 100vh;
        }

        /* Left Panel - Graph Visualization */
        .graph-panel {
            background: #1e293b;
            border-right: 1px solid #334155;
            overflow-y: auto;
            padding: 20px;
        }

        .panel-header {
            font-size: 14px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }

        /* Graph Nodes */
        .graph-container {
            margin-top: 20px;
        }

        .node {
            background: #334155;
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 12px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }

        .node:hover {
            border-color: #667eea;
            background: #3f4b5f;
            transform: translateX(4px);
        }

        .node.active {
            border-color: #667eea;
            background: #2d3748;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        }

        .node.senior-partner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #764ba2;
            color: white;
        }

        .node-title {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .node-description {
            font-size: 12px;
            opacity: 0.8;
        }

        .node-connector {
            width: 2px;
            height: 12px;
            background: #475569;
            margin-left: 20px;
        }

        /* Right Panel - Chat Interface */
        .chat-panel {
            display: flex;
            flex-direction: column;
            background: #0f172a;
        }

        .chat-header {
            background: #1e293b;
            border-bottom: 1px solid #334155;
            padding: 20px 30px;
        }

        .chat-title {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .chat-subtitle {
            font-size: 14px;
            color: #94a3b8;
            margin-top: 4px;
        }

        /* Messages Area */
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
        }

        .message {
            margin-bottom: 20px;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        .message.agent .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .message-name {
            font-weight: 600;
            font-size: 14px;
        }

        .message-content {
            background: #1e293b;
            border-radius: 8px;
            padding: 16px 20px;
            margin-left: 42px;
            line-height: 1.6;
            border-left: 3px solid #334155;
        }

        .message.user .message-content {
            border-left-color: #3b82f6;
        }

        .message.agent .message-content {
            border-left-color: #667eea;
        }

        /* Examples */
        .examples {
            padding: 0 30px 20px;
        }

        .examples-title {
            font-size: 12px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }

        .examples-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }

        .example-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 12px 16px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }

        .example-card:hover {
            border-color: #667eea;
            background: #2d3748;
            transform: translateY(-2px);
        }

        /* Input Area */
        .input-container {
            background: #1e293b;
            border-top: 1px solid #334155;
            padding: 20px 30px;
        }

        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        textarea {
            flex: 1;
            background: #0f172a;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 12px 16px;
            color: #e2e8f0;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
            min-height: 60px;
            max-height: 200px;
            transition: border-color 0.2s;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        textarea::placeholder {
            color: #64748b;
        }

        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 32px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }

        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Loading State */
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #94a3b8;
            font-size: 14px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #334155;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #0f172a;
        }

        ::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }

        /* Stats */
        .stats {
            display: flex;
            gap: 20px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #334155;
            font-size: 12px;
            color: #94a3b8;
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .stat-value {
            color: #667eea;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Left Panel: Graph Visualization -->
        <div class="graph-panel">
            <div class="panel-header">🧠 LawBrain Architecture</div>

            <!-- Senior Partner Node -->
            <div class="node senior-partner" data-agent="senior">
                <div class="node-title">
                    <span>👔</span>
                    <span>Senior Partner</span>
                </div>
                <div class="node-description">Routes cases to specialized lawyers</div>
            </div>

            <div class="node-connector"></div>

            <div class="graph-container">
                <div class="panel-header" style="margin-top: 10px;">Specialized Lawyers</div>

                <div class="node" data-agent="criminal">
                    <div class="node-title">
                        <span>⚖️</span>
                        <span>Criminal Lawyer</span>
                    </div>
                    <div class="node-description">Defense, DUI, white-collar crime</div>
                </div>

                <div class="node" data-agent="civil">
                    <div class="node-title">
                        <span>📋</span>
                        <span>Civil Litigation</span>
                    </div>
                    <div class="node-description">Lawsuits, contracts, torts</div>
                </div>

                <div class="node" data-agent="corporate">
                    <div class="node-title">
                        <span>💼</span>
                        <span>Corporate Lawyer</span>
                    </div>
                    <div class="node-description">Business formation, M&A, contracts</div>
                </div>

                <div class="node" data-agent="ip">
                    <div class="node-title">
                        <span>💡</span>
                        <span>IP Lawyer</span>
                    </div>
                    <div class="node-description">Patents, trademarks, copyrights</div>
                </div>

                <div class="node" data-agent="family">
                    <div class="node-title">
                        <span>👨‍👩‍👧‍👦</span>
                        <span>Family Lawyer</span>
                    </div>
                    <div class="node-description">Divorce, custody, adoption</div>
                </div>

                <div class="node" data-agent="realestate">
                    <div class="node-title">
                        <span>🏠</span>
                        <span>Real Estate Lawyer</span>
                    </div>
                    <div class="node-description">Transactions, leases, zoning</div>
                </div>

                <div class="node" data-agent="employment">
                    <div class="node-title">
                        <span>👔</span>
                        <span>Employment Lawyer</span>
                    </div>
                    <div class="node-description">Workplace issues, discrimination</div>
                </div>

                <div class="node" data-agent="estate">
                    <div class="node-title">
                        <span>📜</span>
                        <span>Estate Planning</span>
                    </div>
                    <div class="node-description">Wills, trusts, probate</div>
                </div>

                <div class="node" data-agent="immigration">
                    <div class="node-title">
                        <span>🌍</span>
                        <span>Immigration Lawyer</span>
                    </div>
                    <div class="node-description">Visas, green cards, citizenship</div>
                </div>
            </div>

            <div class="stats">
                <div class="stat">
                    <span>Agents:</span>
                    <span class="stat-value">10</span>
                </div>
                <div class="stat">
                    <span>Status:</span>
                    <span class="stat-value">🟢 Online</span>
                </div>
            </div>
        </div>

        <!-- Right Panel: Chat Interface -->
        <div class="chat-panel">
            <div class="chat-header">
                <div class="chat-title">🧠 LawBrain Studio</div>
                <div class="chat-subtitle">Full-Service AI Law Firm with 9 Specialized Lawyers</div>
            </div>

            <div class="examples">
                <div class="examples-title">Try These Examples</div>
                <div class="examples-grid">
                    <div class="example-card" onclick="setQuestion('I was arrested for DUI. What should I do?')">
                        🚗 DUI arrest - need advice
                    </div>
                    <div class="example-card" onclick="setQuestion('I want to start an LLC for my tech startup.')">
                        💼 Starting an LLC
                    </div>
                    <div class="example-card" onclick="setQuestion('I need help with a divorce.')">
                        👨‍👩‍👧‍👦 Divorce assistance
                    </div>
                    <div class="example-card" onclick="setQuestion('How do I trademark my brand name?')">
                        💡 Trademark registration
                    </div>
                    <div class="example-card" onclick="setQuestion('My landlord is refusing to return my deposit.')">
                        🏠 Landlord dispute
                    </div>
                    <div class="example-card" onclick="setQuestion('I was fired for reporting safety violations.')">
                        👔 Wrongful termination
                    </div>
                </div>
            </div>

            <div class="messages-container" id="messages">
                <div class="message agent">
                    <div class="message-header">
                        <div class="message-avatar">👔</div>
                        <div class="message-name">Senior Partner</div>
                    </div>
                    <div class="message-content">
                        Welcome to LawBrain! I'm the Senior Partner, and I coordinate our team of 9 specialized lawyers to provide you with expert legal guidance.<br><br>
                        What legal matter can we help you with today?
                    </div>
                </div>
            </div>

            <div class="loading" id="loading">
                <span class="spinner"></span>
                <span>Consulting with our specialist lawyers...</span>
            </div>

            <div class="input-container">
                <div class="input-wrapper">
                    <textarea
                        id="question"
                        placeholder="Type your legal question here..."
                        onkeydown="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); askLawyer(); }"
                    ></textarea>
                    <button onclick="askLawyer()" id="sendBtn">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        console.log('Script loaded successfully');

        const agentEmojis = {
            'CriminalLawyer': '⚖️',
            'CivilLitigationLawyer': '📋',
            'CorporateLawyer': '💼',
            'IPLawyer': '💡',
            'FamilyLawyer': '👨‍👩‍👧‍👦',
            'RealEstateLawyer': '🏠',
            'EmploymentLawyer': '👔',
            'EstatePlanningLawyer': '📜',
            'ImmigrationLawyer': '🌍',
            '__supervisor__': '👔'
        };

        function setQuestion(q) {
            console.log('setQuestion called:', q);
            document.getElementById('question').value = q;
            document.getElementById('question').focus();
        }

        // Test that functions are accessible
        window.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded');
            console.log('askLawyer function exists:', typeof window.askLawyer);
            console.log('setQuestion function exists:', typeof window.setQuestion);

            // Add click listener as backup
            const sendBtn = document.getElementById('sendBtn');
            if (sendBtn) {
                console.log('Send button found, adding backup listener');
                sendBtn.addEventListener('click', function(e) {
                    console.log('Button clicked (backup listener)');
                    if (typeof window.askLawyer === 'function') {
                        window.askLawyer();
                    } else {
                        console.error('askLawyer function not found!');
                    }
                });
            } else {
                console.error('Send button not found!');
            }
        });

        function addMessage(name, content, isUser = false) {
            console.log('addMessage called:', {name, contentLength: content?.length, isUser});

            const messagesContainer = document.getElementById('messages');
            if (!messagesContainer) {
                console.error('Messages container not found!');
                return;
            }

            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'agent'}`;

            // Handle supervisor name
            const actualName = name === 'supervisor' ? '__supervisor__' : name;
            const emoji = isUser ? '👤' : (agentEmojis[actualName] || agentEmojis['__supervisor__'] || '⚖️');
            const displayName = actualName === '__supervisor__' ? 'Senior Partner' :
                               (name === 'supervisor' ? 'Senior Partner' :
                               name.replace(/([A-Z])/g, ' $1').trim().replace('Lawyer', ''));

            const safeContent = (content || '').replace(/\n/g, '<br>');

            messageDiv.innerHTML = `
                <div class="message-header">
                    <div class="message-avatar">${emoji}</div>
                    <div class="message-name">${isUser ? 'You' : displayName}</div>
                </div>
                <div class="message-content">${safeContent}</div>
            `;

            messagesContainer.appendChild(messageDiv);

            // Scroll to bottom
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 10);

            console.log('Message added successfully');

            // Highlight active agent
            if (!isUser) {
                highlightAgent(actualName);
            }
        }

        function highlightAgent(name) {
            document.querySelectorAll('.node').forEach(node => node.classList.remove('active'));

            const agentMap = {
                'CriminalLawyer': 'criminal',
                'CivilLitigationLawyer': 'civil',
                'CorporateLawyer': 'corporate',
                'IPLawyer': 'ip',
                'FamilyLawyer': 'family',
                'RealEstateLawyer': 'realestate',
                'EmploymentLawyer': 'employment',
                'EstatePlanningLawyer': 'estate',
                'ImmigrationLawyer': 'immigration',
                '__supervisor__': 'senior'
            };

            const agentType = agentMap[name];
            if (agentType) {
                const node = document.querySelector(`[data-agent="${agentType}"]`);
                if (node) {
                    node.classList.add('active');
                    setTimeout(() => node.classList.remove('active'), 2000);
                }
            }
        }

        window.askLawyer = async function() {
            console.log('askLawyer called');
            const question = document.getElementById('question').value;
            console.log('Question:', question);

            if (!question.trim()) {
                alert('Please enter a question');
                return;
            }

            const btn = document.getElementById('sendBtn');
            const loading = document.getElementById('loading');
            const questionInput = document.getElementById('question');

            btn.disabled = true;
            loading.classList.add('show');

            // Add user message
            console.log('Adding user message');
            addMessage('User', question, true);
            questionInput.value = '';

            try {
                console.log('Sending request to /ask');
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });

                console.log('Response status:', res.status);
                const data = await res.json();
                console.log('Response data:', data);

                if (data.error) {
                    console.error('Error from server:', data.error);
                    addMessage('Error', data.error, false);
                } else {
                    console.log('Processing messages:', data.messages.length);
                    // Add all agent responses
                    let addedCount = 0;
                    data.messages.forEach(msg => {
                        console.log('Message:', msg.type, msg.name, msg.content?.substring(0, 50));
                        if (msg.type !== 'humanmessage') {
                            addMessage(msg.name || 'supervisor', msg.content, false);
                            addedCount++;
                        }
                    });
                    console.log('Added', addedCount, 'messages');

                    // If no messages were added, show a default response
                    if (addedCount === 0) {
                        console.warn('No messages to display');
                        addMessage('System', 'No response received. Please try again.', false);
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                addMessage('Error', 'Failed to get response: ' + error.message, false);
            } finally {
                btn.disabled = false;
                loading.classList.remove('show');
                console.log('Request complete');
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

@flask_app.route('/graph')
def graph():
    """Return graph structure for visualization"""
    try:
        graph_data = {
            'nodes': [
                {'id': 'senior', 'type': 'supervisor', 'label': 'Senior Partner'},
                {'id': 'criminal', 'type': 'agent', 'label': 'Criminal Lawyer'},
                {'id': 'civil', 'type': 'agent', 'label': 'Civil Litigation'},
                {'id': 'corporate', 'type': 'agent', 'label': 'Corporate Lawyer'},
                {'id': 'ip', 'type': 'agent', 'label': 'IP Lawyer'},
                {'id': 'family', 'type': 'agent', 'label': 'Family Lawyer'},
                {'id': 'realestate', 'type': 'agent', 'label': 'Real Estate'},
                {'id': 'employment', 'type': 'agent', 'label': 'Employment Lawyer'},
                {'id': 'estate', 'type': 'agent', 'label': 'Estate Planning'},
                {'id': 'immigration', 'type': 'agent', 'label': 'Immigration Lawyer'}
            ],
            'edges': [
                {'from': 'senior', 'to': 'criminal'},
                {'from': 'senior', 'to': 'civil'},
                {'from': 'senior', 'to': 'corporate'},
                {'from': 'senior', 'to': 'ip'},
                {'from': 'senior', 'to': 'family'},
                {'from': 'senior', 'to': 'realestate'},
                {'from': 'senior', 'to': 'employment'},
                {'from': 'senior', 'to': 'estate'},
                {'from': 'senior', 'to': 'immigration'}
            ]
        }
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧠 LawBrain Studio - Enhanced Interface Starting...")
    print("="*60)
    print("\n📍 Access at: http://localhost:8081")
    print("\n✨ Features:")
    print("   • Visual graph of all agents")
    print("   • Real-time agent highlighting")
    print("   • Modern Studio-like UI")
    print("   • Dark theme")
    print("   • Message flow visualization")
    print("\n🔒 Press CTRL+C to stop\n")
    flask_app.run(host='0.0.0.0', port=8081, debug=False)
