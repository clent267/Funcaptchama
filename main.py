from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

ROBLOX_PUBLIC_KEY = "476068BF-9607-4799-B53D-966BE98E2B81"
ARKOSE_SURL = "https://roblox-api.arkoselabs.com"

@app.route('/')
def home():
    return "BUHAY AKO! 💪 Kung magpapagawa kayo, DM SELB"

@app.route('/ping')
def ping():
    return "OK"

@app.route('/roblox-login', methods=['GET'])
def roblox_login_page():
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Real Roblox Login + FunCaptcha</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #111; color: white; padding: 20px; text-align: center; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            #funcaptcha-container {{ border: 1px solid #444; width: 100%; max-width: 700px; height: 620px; margin: 20px auto; }}
            input, button {{ padding: 12px; margin: 8px; width: 80%; max-width: 400px; font-size: 16px; }}
            pre {{ background: #1a1a1a; padding: 15px; text-align: left; overflow: auto; max-height: 600px; }}
        </style>
        <script src="{ARKOSE_SURL}/v2/{ROBLOX_PUBLIC_KEY}/api.js" async defer></script>
    </head>
    <body>
        <div class="container">
            <h2>Real Roblox FunCaptcha + Challenge</h2>
            
            <div id="funcaptcha-container"></div>
            <div id="status">Loading real challenge...</div>

            <h3>Credentials</h3>
            <input type="text" id="username" placeholder="Username / Email" /><br>
            <input type="password" id="password" placeholder="Password" /><br>
            <button onclick="startRealLoginFlow()">Start Login Flow</button>

            <pre id="result"></pre>
        </div>

        <script>
            let captchaToken = "";
            let enforcementObject = null;

            function setupEnforcement(myEnforcement) {{
                enforcementObject = myEnforcement;
                enforcementObject.setConfig({{
                    selector: '#funcaptcha-container',
                    onCompleted: function(response) {{
                        captchaToken = response.token;
                        document.getElementById('status').innerHTML = `✅ FunCaptcha Solved!`;
                    }}
                }});
                enforcementObject.run();
            }}
            window.setupEnforcement = setupEnforcement;

            async function startRealLoginFlow() {{
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value.trim();
                const resultEl = document.getElementById('result');

                if (!username || !password) return resultEl.textContent = "Enter username & password";
                if (!captchaToken) return resultEl.textContent = "Solve captcha first!";

                resultEl.textContent = "Sending login request...\n";

                try {{
                    const res = await fetch('https://auth.roblox.com/v2/login', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            ctype: "Username",
                            cvalue: username,
                            password: password,
                            captchaToken: captchaToken,
                            captchaProvider: "PROVIDER_ARKOS_LABS"
                        }})
                    }});
                    const data = await res.json();
                    resultEl.textContent += JSON.stringify(data, null, 2);
                }} catch(e) {{
                    resultEl.textContent += "Error: " + e.message;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))            <small>💡 Connect Urban VPN first for better success</small>

            <div id="funcaptcha-container"></div>

            <div id="status">Loading real Roblox challenge...</div>

            <h3>Credentials</h3>
            <input type="text" id="username" placeholder="Username / Email" /><br>
            <input type="password" id="password" placeholder="Password" /><br>
            <button onclick="startRealLoginFlow()">🚀 Start Real Login Flow</button>

            <pre id="result"></pre>
        </div>

        <script>
            let captchaToken = "";
            let enforcementObject = null;

            function setupEnforcement(myEnforcement) {{
                enforcementObject = myEnforcement;
                enforcementObject.setConfig({{
                    selector: '#funcaptcha-container',
                    onCompleted: function(response) {{
                        captchaToken = response.token;
                        document.getElementById('status').innerHTML = `✅ FunCaptcha Solved! Token Ready.`;
                        console.log("✅ Token:", captchaToken);
                    }},
                    onError: function(error) {{ 
                        document.getElementById('status').innerHTML = `❌ Arkose Error: ${{error}}`; 
                    }}
                }});
                enforcementObject.run();
            }}
            window.setupEnforcement = setupEnforcement;

            async function startRealLoginFlow() {{
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value.trim();
                const resultEl = document.getElementById('result');

                if (!username || !password) {{
                    resultEl.textContent = "❌ Please enter username and password!";
                    return;
                }}
                if (!captchaToken) {{
                    resultEl.textContent = "❌ Solve the FunCaptcha first!";
                    return;
                }}

                resultEl.textContent = "Step 1: Triggering real Roblox challenge...\\n";

                try {{
                    // Trigger challenge
                    const initRes = await fetch('https://auth.roblox.com/v2/login', {{
                        method: 'POST',
                        headers: {{ 
                            'Content-Type': 'application/json',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        }},
                        body: JSON.stringify({{
                            ctype: "Username",
                            cvalue: username,
                            password: password
                        }})
                    }});

                    let challengeId = initRes.headers.get('rblx-challenge-id') || initRes.headers.get('x-challenge-id') || "";
                    let challengeMetadata = initRes.headers.get('rblx-challenge-metadata') || "";
                    let blob = "";

                    if (challengeMetadata) {{
                        try {{
                            const decoded = JSON.parse(atob(challengeMetadata));
                            blob = decoded.blob || "";
                        }} catch(e) {{}}
                    }}

                    resultEl.textContent += `✅ Challenge ID: ${{challengeId}}\\n`;
                    if (blob) resultEl.textContent += `✅ Blob Loaded\\n`;

                    // Final Login
                    resultEl.textContent += "Step 2: Sending final login with Token + Blob...\\n";

                    const finalBody = {{
                        ctype: "Username",
                        cvalue: username,
                        password: password,
                        captchaToken: captchaToken,
                        captchaProvider: "PROVIDER_ARKOS_LABS",
                        challengeId: challengeId
                    }};

                    if (challengeMetadata) finalBody.challengeMetadata = challengeMetadata;

                    const loginRes = await fetch('https://auth.roblox.com/v2/login', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                            'X-CSRF-TOKEN': initRes.headers.get('x-csrf-token') || "",
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        }},
                        body: JSON.stringify(finalBody)
                    }});

                    const data = await loginRes.json();
                    resultEl.textContent += "\\n=== FINAL RESPONSE ===\\n" + JSON.stringify(data, null, 2);

                }} catch (err) {{
                    resultEl.textContent += "Error: " + err.message;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

# Keep your other endpoints
@app.route('/send-visit', methods=['GET','POST'])
def visit_embed():
    return jsonify({"status": "success", "message": "Visit OK"})

@app.route('/send-result', methods=['GET','POST'])
def result_embed():
    return jsonify({"status": "success", "message": "Result OK"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
