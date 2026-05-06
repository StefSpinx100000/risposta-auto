from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import json
import os
from datetime import datetime

app = FastAPI()

# ═══════════════ CONFIGURAZIONE ═══════════════
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

# ═══════════════ FUNZIONI AI ═══════════════

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

# ═══════════════ WEBHOOK WHATSAPP ═══════════════

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

# ═══════════════ PAGINA DEMO ═══════════════

@app.get("/")
async def home():
    html_content = """
    <html>
    <head><title>Risposta-Auto - Demo</title></head>
    <body style="font-family: sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
        <h1>🤖 Risposta-Auto</h1>
        <p>Risponditore automatico WhatsApp per attività locali</p>
        <div style="background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 30px 0;">
            <p><strong>Prova la demo:</strong></p>
            <input id="msg" type="text" placeholder="Scrivi un messaggio..." style="padding: 10px; width: 70%;">
            <button onclick="test()" style="padding: 10px 20px;">Invia</button>
            <p id="risposta" style="margin-top: 20px; font-style: italic;"></p>
        </div>
        <p style="color: gray;">Collegato a WhatsApp Business API</p>
        <script>
        async function test() {
            let msg = document.getElementById('msg').value;
            let r = await fetch('/test?msg=' + encodeURIComponent(msg));
            let data = await r.json();
            document.getElementById('risposta').innerText = '🤖 ' + data.risposta;
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
