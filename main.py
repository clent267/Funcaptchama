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
        <title>Roblox Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #111; color: white; padding: 20px; text-align: center; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            #funcaptcha-container {{ border: 2px solid #555; width: 100%; max-width: 700px; height: 580px; margin: 20px auto; }}
            input, button {{ padding: 12px; margin: 8px; width: 80%; max-width: 400px; font-size: 16px; }}
            pre {{ background: #1a1a1a; padding: 15px; text-align: left; max-height: 500px; overflow: auto; }}
        </style>
        <script src="{ARKOSE_SURL}/v2/{ROBLOX_PUBLIC_KEY}/api.js" async defer></script>
    </head>
    <body>
        <div class="container">
            <h2>Real Roblox FunCaptcha Login</h2>
            
            <div id="funcaptcha-container"></div>
            <div id="status">Loading real challenge... (solve the captcha)</div>

            <h3>Credentials</h3>
            <input type="text" id="username" placeholder="Username / Email" /><br>
            <input type="password" id="password" placeholder="Password" /><br>
            <button onclick="startLogin()">🚀 Login to Roblox</button>

            <pre id="result"></pre>
        </div>

        <script>
            let token = "";

            function setupEnforcement(e) {{
                e.setConfig({{
                    selector: '#funcaptcha-container',
                    onCompleted: function(r) {{
                        token = r.token;
                        document.getElementById('status').innerHTML = '✅ FunCaptcha Solved!';
                    }},
                    onError: function(err) {{ 
                        document.getElementById('status').innerHTML = '❌ Error: ' + err;
                    }}
                }});
                e.run();
            }}
            window.setupEnforcement = setupEnforcement;

            async function startLogin() {{
                const user = document.getElementById('username').value.trim();
                const pass = document.getElementById('password').value.trim();
                const resEl = document.getElementById('result');

                if (!user || !pass) return resEl.textContent = "❌ Enter username and password";
                if (!token) return resEl.textContent = "❌ Solve the captcha first!";

                resEl.textContent = "Sending login request to Roblox...\\n";

                try {{
                    const resp = await fetch('https://auth.roblox.com/v2/login', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            ctype: "Username",
                            cvalue: user,
                            password: pass,
                            captchaToken: token,
                            captchaProvider: "PROVIDER_ARKOS_LABS"
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
