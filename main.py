"""
RISPOSTA-AUTO - Risponditore WhatsApp con AI
Per negozi, ristoranti, attività locali
Gratuito, in italiano, semplice
"""

from fastapi import FastAPI, Request
import requests
import json
import os
from datetime import datetime

app = FastAPI()

# ═══════════════ CONFIGURAZIONE ═══════════════
# Sostituisci con i tuoi dati da Meta Developers
WHATSAPP_TOKEN = "IL_TUO_TOKEN_QUI"
PHONE_NUMBER_ID = "IL_TUO_PHONE_NUMBER_ID"
VERIFY_TOKEN = "nest_verify_token_123"

# Informazioni dell'attività (cambiale con quelle del primo negozio che testi)
INFO_ATTIVITA = """
Sei l'assistente virtuale di "Pizzeria Da Mario".
Orari: 12:00-15:00 e 19:00-23:30. Chiuso Lunedì.
Menù: pizze da 6€ a 12€, anche senza glutine.
Consegna a domicilio: solo in zona, 2€ extra.
Pagamenti: contanti, carta, Satispay.
Parcheggio: gratuito in strada.
"""

# Memoria delle conversazioni (in produzione usa un database)
memoria_clienti = {}

# ═══════════════ FUNZIONI AI ═══════════════

def chiedi_a_chatgpt(messaggio_cliente, cronologia=None):
    """
    Usa ChatGPT per rispondere in modo naturale al cliente.
    Costa circa 0.001€ a messaggio.
    """
    try:
        # Se non hai OpenAI, rispondi con regole semplici
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
        # Fallback senza OpenAI - risposte basiche ma funzionanti
        return rispondi_base(messaggio_cliente)

def rispondi_base(messaggio):
    """Risposte semplici senza AI. Funziona offline."""
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
    """Meta verifica che il webhook sia tuo"""
    params = request.query_params
    
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge", 0))
    return {"error": "Token non valido"}

@app.post("/webhook")
async def ricevi_messaggi(request: Request):
    """Riceve messaggi WhatsApp e risponde"""
    data = await request.json()
    
    try:
        # Estrai messaggio
        messaggio = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero_cliente = messaggio["from"]
        testo_ricevuto = messaggio["text"]["body"]
        
        print(f"\n📩 Messaggio da {numero_cliente}: {testo_ricevuto}")
        
        # Costruisci risposta
        cronologia = memoria_clienti.get(numero_cliente, [])
        risposta = chiedi_a_chatgpt(testo_ricevuto, cronologia)
        
        # Salva in memoria
        cronologia.append({"ruolo": "cliente", "testo": testo_ricevuto})
        cronologia.append({"ruolo": "assistente", "testo": risposta})
        memoria_clienti[numero_cliente] = cronologia[-5:]  # Tieni ultimi 5 messaggi
        
        print(f"📤 Risposta: {risposta}")
        
        # Invia risposta su WhatsApp
        invia_messaggio_whatsapp(numero_cliente, risposta)
        
    except Exception as e:
        print(f"Errore: {e}")
    
    return {"status": "ok"}

def invia_messaggio_whatsapp(numero, testo):
    """Invia un messaggio WhatsApp via API Meta"""
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
    return """
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

@app.get("/test")
async def test(msg: str = ""):
    risposta = chiedi_a_chatgpt(msg)
    return {"messaggio": msg, "risposta": risposta}

# ═══════════════ AVVIO ═══════════════

if __name__ == "__main__":
    import uvicorn
    print("""
    ╔══════════════════════════════════╗
    ║   RISPOSTA-AUTO                 ║
    ║   WhatsApp AI Responder         ║
    ║   Avviato su http://0.0.0.0:8080║
    ╚══════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8080)
