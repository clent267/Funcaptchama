from flask import Flask, render_template_string
import os

app = Flask(__name__)

ROBLOX_PUBLIC_KEY = "476068BF-9607-4799-B53D-966BE98E2B81"
ARKOSE_SURL = "https://roblox-api.arkoselabs.com"

@app.route('/')
def home():
    return "BUHAY AKO! 💪 DM SELB"

@app.route('/roblox-login')
def roblox_login_page():
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Roblox Login Flow</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #111; color: white; padding: 20px; text-align: center; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            iframe {{ border: 2px solid #555; width: 100%; max-width: 700px; height: 620px; margin: 20px auto; display: block; }}
            input, button {{ padding: 12px; margin: 8px; width: 80%; max-width: 400px; font-size: 16px; }}
            pre {{ background: #1a1a1a; padding: 15px; text-align: left; max-height: 500px; overflow: auto; }}
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
                <iframe id="captcha-iframe" 
                        src="" 
                        allow="fullscreen">
                </iframe>
            </div>

            <button onclick="startFinalLogin()" style="margin-top:15px;">2. Send Final Login</button>

            <pre id="result"></pre>
        </div>

        <script>
            let captchaToken = "";
            let challengeId = "";

            async function triggerChallenge() {{
                const user = document.getElementById('username').value.trim();
                const pass = document.getElementById('password').value.trim();
                const resEl = document.getElementById('result');

                if (!user || !pass) return resEl.textContent = "Enter username and password first!";

                resEl.textContent = "Triggering Roblox challenge...\n";

                try {{
                    const resp = await fetch('https://auth.roblox.com/v2/login', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            ctype: "Username",
                            cvalue: user,
                            password: pass
                        }})
                    }});

                    challengeId = resp.headers.get('rblx-challenge-id') || "";
                    resEl.textContent += "Challenge triggered! Loading captcha...\n";

                    // Load real captcha iframe
                    const iframe = document.getElementById('captcha-iframe');
                    iframe.src = `https://iframe.arkoselabs.com/\( {ROBLOX_PUBLIC_KEY}/index.html?surl= \){ARKOSE_SURL}`;
                    document.getElementById('captcha-section').style.display = 'block';

                }} catch(err) {{
                    resEl.textContent += "Error: " + err.message;
                }}
            }}

            // Listen for captcha token
            window.addEventListener('message', function(e) {{
                if (e.origin.includes('arkoselabs.com')) {{
                    captchaToken = e.data;
                    document.getElementById('result').textContent += "✅ Captcha Token Received!\n";
                }}
            }});

            async function startFinalLogin() {{
                const user = document.getElementById('username').value.trim();
                const pass = document.getElementById('password').value.trim();
                const resEl = document.getElementById('result');

                if (!captchaToken) return resEl.textContent += "❌ Solve captcha first!";

                resEl.textContent += "Sending final login with token...\n";

                try {{
                    const resp = await fetch('https://auth.roblox.com/v2/login', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            ctype: "Username",
                            cvalue: user,
                            password: pass,
                            captchaToken: captchaToken,
                            captchaProvider: "PROVIDER_ARKOS_LABS",
                            challengeId: challengeId
                        }})
                    }});

                    const data = await resp.json();
                    resEl.textContent += JSON.stringify(data, null, 2);
                }} catch(err) {{
                    resEl.textContent += "Error: " + err.message;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
