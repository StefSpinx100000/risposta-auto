from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import json
import os
from datetime import datetime

app = FastAPI()

WHATSAPP_TOKEN = "IL_TUO_TOKEN_QUI"
PHONE_NUMBER_ID = "IL_TUO_PHONE_NUMBER_ID"
VERIFY_TOKEN = "nest_verify_token_123"

INFO_ATTIVITA = """
Sei l'assistente virtuale di "Pizzeria Da Mario".
Orari: 12:00-15:00 e 19:00-23:30. Chiuso Lunedì.
Menù: pizze da 6€ a 12€, anche senza glutine.
Consegna a domicilio: solo in zona, 2€ extra.
Pagamenti: contanti, carta, Satispay.
Parcheggio: gratuito in strada.
"""

memoria_clienti = {}

def chiedi_a_chatgpt(messaggio_cliente, cronologia=None):
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY", "la-tua-chiave-qui")
        contesto = f"{INFO_ATTIVITA}\n\nCronologia recente: {cronologia}\n\nCliente scrive: {messaggio_cliente}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sei un assistente cordiale di una pizzeria. Rispondi in italiano, in modo breve e utile. Se non sai qualcosa, dì 'Chiedo al titolare e le faccio sapere'."},
                {"role": "user", "content": contesto}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except:
        return rispondi_base(messaggio_cliente)

def rispondi_base(messaggio):
    msg = messaggio.lower()
    if any(word in msg for word in ["orari", "aperto", "aprite", "chiuso"]):
        return "Siamo aperti 12:00-15:00 e 19:00-23:30. Chiusi il Lunedì. Posso prenotarle un tavolo?"
    elif any(word in msg for word in ["menù", "menu", "prezzi", "costo"]):
        return "Le nostre pizze vanno da 6€ a 12€. Abbiamo anche opzioni senza glutine. Vuole che le invii il menù completo?"
    elif any(word in msg for word in ["prenotare", "prenotazione", "tavolo"]):
        return "Certo! Per quando vorrebbe prenotare? Mi dica giorno e orario e verifico disponibilità."
    elif any(word in msg for word in ["consegna", "domicilio", "portate"]):
        return "Facciamo consegna a domicilio in zona (2€ extra). Mi dica l'indirizzo e verifico se siamo coperti."
    elif any(word in msg for word in ["senza glutine", "celiaco", "glutine"]):
        return "Sì, abbiamo pizze senza glutine certificate AIC! Tutte le nostre pizze possono essere preparate senza glutine."
    else:
        return "Grazie per averci contattato! Come posso aiutarla? Mi dica pure cosa le serve."

@app.get("/webhook")
async def verifica_webhook(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge", 0))
    return {"error": "Token non valido"}

@app.post("/webhook")
async def ricevi_messaggi(request: Request):
    data = await request.json()
    try:
        messaggio = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero_cliente = messaggio["from"]
        testo_ricevuto = messaggio["text"]["body"]
        cronologia = memoria_clienti.get(numero_cliente, [])
        risposta = chiedi_a_chatgpt(testo_ricevuto, cronologia)
        cronologia.append({"ruolo": "cliente", "testo": testo_ricevuto})
        cronologia.append({"ruolo": "assistente", "testo": risposta})
        memoria_clienti[numero_cliente] = cronologia[-5:]
        invia_messaggio_whatsapp(numero_cliente, risposta)
    except Exception as e:
        print(f"Errore: {e}")
    return {"status": "ok"}

def invia_messaggio_whatsapp(numero, testo):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": testo}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

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
                word-wrap: break-word;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .message.user {
                background: #1a1a2e;
                color: #ccc;
                margin-right: auto;
            }
            .message.bot {
                background: linear-gradient(135deg, #25D366, #00cc55);
                color: #0a0a0a;
                font-weight: 600;
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
            <p class="footer-text">Collegato a WhatsApp Business API &middot; Risposte in tempo reale</p>
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

@app.get("/test")
async def test(msg: str = ""):
    risposta = chiedi_a_chatgpt(msg)
    return {"messaggio": msg, "risposta": risposta}
