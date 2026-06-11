
from flask import Flask, render_template_string, request, jsonify, session
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

# Real Roblox API endpoints
ROBLOX_AUTH_API = "https://auth.roblox.com"
ROBLOX_API = "https://www.roblox.com"

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
                max-width: 500px; 
                height: 500px; 
                margin: 20px auto; 
                display: block; 
                background: white;
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
            button:disabled {
                background: #333;
                cursor: not-allowed;
            }
            pre { 
                background: #1a1a1a; 
                padding: 15px; 
                text-align: left; 
                max-height: 500px; 
                overflow: auto;
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 12px;
            }
            .success { color: #00ff00; }
            .error { color: #ff4444; }
            .info { color: #00aaff; }
            .section {
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #333;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Roblox Real Login Flow</h1>
            
            <div class="section">
                <h3>Step 1: Enter Credentials</h3>
                <input type="text" id="username" placeholder="Username or Email" /><br>
                <input type="password" id="password" placeholder="Password" /><br>
                <button onclick="stepOne()">Start Login Process</button>
            </div>

            <div id="captcha-section" style="display:none;" class="section">
                <h3>Step 2: Solve Captcha</h3>
                <p>Complete the captcha challenge below:</p>
                <div id="captcha-container"></div>
            </div>

            <div id="login-section" style="display:none;" class="section">
                <h3>Step 3: Complete Login</h3>
                <button onclick="stepThree()">Finalize Login</button>
            </div>

            <pre id="result"></pre>
        </div>

        <script src="https://client-api.arkoselabs.com/v2/client.js"></script>
        <script>
            let captchaToken = "";
            let challengeMetadata = null;
            let username = "";
            let password = "";

            function log(msg, type = 'info') {
                const resEl = document.getElementById('result');
                const timestamp = new Date().toLocaleTimeString();
                const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
                resEl.textContent += `[${timestamp}] ${prefix} ${msg}\\n`;
                resEl.scrollTop = resEl.scrollHeight;
            }

            async function stepOne() {
                username = document.getElementById('username').value.trim();
                password = document.getElementById('password').value.trim();
                
                if (!username || !password) {
                    log('Please enter username and password', 'error');
                    return;
                }

                log('Initiating login request...', 'info');

                try {
                    const resp = await fetch('/api/initiate-login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });

                    const data = await resp.json();

                    if (!resp.ok) {
                        log(`Login init failed: ${data.error}`, 'error');
                        return;
                    }

                    if (data.challengeRequired) {
                        log('Captcha challenge required', 'info');
                        challengeMetadata = data.metadata;
                        loadCaptcha(data.metadata);
                        document.getElementById('captcha-section').style.display = 'block';
                    } else if (data.success) {
                        log('Login successful!', 'success');
                        log(JSON.stringify(data.user, null, 2), 'success');
                    }

                } catch(err) {
                    log(`Error: ${err.message}`, 'error');
                }
            }

            function loadCaptcha(metadata) {
                log('Loading Arkose captcha...', 'info');
                
                if (typeof ARKOSE === 'undefined') {
                    log('Arkose SDK not loaded', 'error');
                    return;
                }

                const container = document.getElementById('captcha-container');
                container.innerHTML = '';

                ARKOSE.setConfig({
                    variant: 'default',
                    onCompleted: onCaptchaComplete,
                    onError: onCaptchaError,
                    onReady: () => {
                        log('Captcha widget ready', 'success');
                    }
                });

                try {
                    const loader = new ARKOSE.EngineLoader(
                        metadata.publicKey,
                        metadata.surl,
                        {
                            target: container,
                            onCompleted: onCaptchaComplete,
                            onError: onCaptchaError
                        }
                    );
                } catch(err) {
                    log(`Captcha load error: ${err.message}`, 'error');
                }
            }

            function onCaptchaComplete(response) {
                log('Captcha solved!', 'success');
                captchaToken = response.token || response;
                log(`Token received (${captchaToken.substring(0, 20)}...)`, 'success');
                document.getElementById('login-section').style.display = 'block';
            }

            function onCaptchaError(error) {
                log(`Captcha error: ${error}`, 'error');
            }

            async function stepThree() {
                if (!captchaToken) {
                    log('No captcha token. Solve captcha first.', 'error');
                    return;
                }

                log('Sending final login with captcha token...', 'info');

                try {
                    const resp = await fetch('/api/complete-login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username,
                            password,
                            captchaToken,
                            challengeMetadata
                        })
                    });

                    const data = await resp.json();

                    if (!resp.ok) {
                        log(`Login failed: ${data.error}`, 'error');
                        if (data.details) {
                            log(JSON.stringify(data.details, null, 2), 'error');
                        }
                        return;
                    }

                    log('✅ LOGIN SUCCESSFUL! 🎉', 'success');
                    log(JSON.stringify(data, null, 2), 'success');

                } catch(err) {
                    log(`Error: ${err.message}`, 'error');
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/initiate-login', methods=['POST'])
def initiate_login():
    """
    Step 1: Initiate login and check if captcha is required
    This mimics the real Roblox login flow
    """
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Step 1: Get login metadata from Roblox
        # First, we need to get the CSRF token
        log_msg = f"[{datetime.now()}] Fetching login page for CSRF token\n"
        
        session_obj = requests.Session()
        
        # Get CSRF token
        csrf_resp = session_obj.get(f"{ROBLOX_AUTH_API}/v2/login")
        csrf_token = csrf_resp.headers.get('x-csrf-token', '')
        
        log_msg += f"[{datetime.now()}] CSRF token obtained\n"

        # Step 2: Attempt login - this should trigger a challenge if needed
        login_payload = {
            'ctype': 'Username',
            'cvalue': username,
            'password': password
        }

        headers = {
            'x-csrf-token': csrf_token,
            'Content-Type': 'application/json'
        }

        login_resp = session_obj.post(
            f"{ROBLOX_AUTH_API}/v2/login",
            json=login_payload,
            headers=headers,
            allow_redirects=False,
            timeout=15
        )

        log_msg += f"[{datetime.now()}] Login response: {login_resp.status_code}\n"

        response_data = {}
        try:
            response_data = login_resp.json()
        except:
            pass

        # Check for challenge/captcha requirement
        if login_resp.status_code == 403:
            # Captcha required
            challenge_id = login_resp.headers.get('rblx-challenge-id', '')
            challenge_metadata = login_resp.headers.get('rblx-challenge-metadata', '')
            
            log_msg += f"[{datetime.now()}] Captcha challenge required\n"

            return jsonify({
                'challengeRequired': True,
                'metadata': {
                    'publicKey': '476068BF-9607-4799-B53D-966BE98E2B81',
                    'surl': 'https://roblox-api.arkoselabs.com',
                    'challengeId': challenge_id,
                    'challengeMetadata': challenge_metadata
                },
                'sessionCookie': session_obj.cookies.get_dict(),
                'logs': log_msg
            }), 200

        elif login_resp.status_code == 200:
            # Successful login without captcha
            log_msg += f"[{datetime.now()}] Login successful\n"
            return jsonify({
                'success': True,
                'user': response_data.get('user', {}),
                'logs': log_msg
            }), 200

        else:
            # Other error
            return jsonify({
                'error': response_data.get('message', 'Login failed'),
                'status': login_resp.status_code,
                'details': response_data,
                'logs': log_msg
            }), login_resp.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout - Roblox API not responding'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/complete-login', methods=['POST'])
def complete_login():
    """
    Step 2: Complete login with captcha token
    """
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        captcha_token = data.get('captchaToken', '').strip()
        challenge_metadata = data.get('challengeMetadata', {})

        if not all([username, password, captcha_token]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create new session for final login
        session_obj = requests.Session()

        # Get fresh CSRF token
        csrf_resp = session_obj.get(f"{ROBLOX_AUTH_API}/v2/login")
        csrf_token = csrf_resp.headers.get('x-csrf-token', '')

        # Prepare final login payload with captcha
        login_payload = {
            'ctype': 'Username',
            'cvalue': username,
            'password': password,
            'captchaToken': captcha_token,
            'captchaProvider': 'PROVIDER_ARKOS_LABS'
        }

        # Add challenge ID if available
        if challenge_metadata.get('challengeId'):
            login_payload['challengeId'] = challenge_metadata['challengeId']

        headers = {
            'x-csrf-token': csrf_token,
            'Content-Type': 'application/json'
        }

        # Send final login request
        login_resp = session_obj.post(
            f"{ROBLOX_AUTH_API}/v2/login",
            json=login_payload,
            headers=headers,
            allow_redirects=False,
            timeout=15
        )

        response_data = {}
        try:
            response_data = login_resp.json()
        except:
            pass

        if login_resp.status_code == 200:
            # Extract user info and session
            user_info = response_data.get('user', {})
            
            # Get cookies for session validation
            cookies = session_obj.cookies.get_dict()

            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'id': user_info.get('id'),
                    'name': user_info.get('name'),
                    'displayName': user_info.get('displayName'),
                    'email': user_info.get('email'),
                },
                'sessionCookies': cookies,
                'fullResponse': response_data
            }), 200
        else:
            return jsonify({
                'error': response_data.get('message', 'Login failed'),
                'status': login_resp.status_code,
                'details': response_data
            }), login_resp.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
