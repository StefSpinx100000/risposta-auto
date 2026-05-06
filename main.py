@app.get("/")
async def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Risposta-Auto - Demo</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                max-width: 700px;
                width: 100%;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 30px;
                padding: 50px 40px;
                backdrop-filter: blur(20px);
                box-shadow: 0 30px 60px rgba(0,0,0,0.4);
            }
            
            .badge {
                display: inline-block;
                background: rgba(37, 211, 102, 0.15);
                border: 1px solid rgba(37, 211, 102, 0.3);
                color: #25D366;
                padding: 8px 20px;
                border-radius: 50px;
                font-weight: 600;
                font-size: 0.85em;
                margin-bottom: 20px;
            }
            
            h1 {
                font-size: 2.8em;
                font-weight: 900;
                background: linear-gradient(135deg, #fff, #25D366);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #888;
                font-size: 1.1em;
                margin-bottom: 40px;
            }
            
            .chat-box {
                background: rgba(0,0,0,0.4);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 20px;
                min-height: 100px;
                max-height: 300px;
                overflow-y: auto;
            }
            
            .message {
                padding: 12px 18px;
                border-radius: 18px;
                margin-bottom: 10px;
                max-width: 80%;
                animation: slideIn 0.3s ease-out;
            }
            
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.user {
                background: #1a1a2e;
                color: #ccc;
                align-self: flex-start;
                margin-right: auto;
            }
            
            .message.bot {
                background: linear-gradient(135deg, #25D366, #00cc55);
                color: #0a0a0a;
                font-weight: 600;
                align-self: flex-end;
                margin-left: auto;
            }
            
            .input-area {
                display: flex;
                gap: 10px;
            }
            
            input {
                flex: 1;
                padding: 16px 20px;
                border-radius: 50px;
                border: 1px solid rgba(255,255,255,0.1);
                background: rgba(0,0,0,0.4);
                color: white;
                font-size: 1em;
                outline: none;
                transition: border 0.3s;
            }
            
            input:focus {
                border-color: #25D366;
            }
            
            input::placeholder {
                color: #555;
            }
            
            button {
                padding: 16px 30px;
                border-radius: 50px;
                border: none;
                background: linear-gradient(135deg, #25D366, #00ff88);
                color: #0a0a0a;
                font-weight: 700;
                font-size: 1em;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 30px rgba(37, 211, 102, 0.4);
            }
            
            .footer-text {
                text-align: center;
                color: #555;
                font-size: 0.8em;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">🤖 Demo Dal Vivo</div>
            <h1>Risposta-Auto</h1>
            <p class="subtitle">Provalo ora. Scrivi un messaggio come se fossi un cliente.</p>
            
            <div class="chat-box" id="chat"></div>
            
            <div class="input-area">
                <input id="msg" type="text" placeholder="Es: Avete posto stasera?" onkeypress="if(event.key==='Enter') test()">
                <button onclick="test()">Invia</button>
            </div>
            
            <p class="footer-text">Collegato a WhatsApp Business API · Risposte in tempo reale</p>
        </div>
        
        <script>
            async function test() {
                let input = document.getElementById('msg');
                let msg = input.value.trim();
                if (!msg) return;
                
                let chat = document.getElementById('chat');
                chat.innerHTML += '<div class="message user">' + msg + '</div>';
                input.value = '';
                chat.scrollTop = chat.scrollHeight;
                
                let r = await fetch('/test?msg=' + encodeURIComponent(msg));
                let data = await r.json();
                
                chat.innerHTML += '<div class="message bot">' + data.risposta + '</div>';
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
