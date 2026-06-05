from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

CHAVE_GROQ = os.environ.get("CHAVE_GROQ")

PERSONALIDADE = """
És o SaúdeBot, assistente de saúde virtual para Moçambique.
Respondes SEMPRE em português de Moçambique.
Respostas curtas e claras — máximo 3 parágrafos.
Sugeres sempre consultar um médico para casos graves.
"""

def groq_responde(mensagem):
    resposta = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {CHAVE_GROQ}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": PERSONALIDADE},
                {"role": "user", "content": mensagem}
            ],
            "max_tokens": 300
        }
    )
    dados = resposta.json()
    if "choices" in dados:
        return dados["choices"][0]["message"]["content"]
    return "Erro na ligação. Tenta novamente."

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    mensagem = request.form.get('Body', '')
    numero = request.form.get('From', '')
    print(f"Mensagem de {numero}: {mensagem}")
    resposta_ia = groq_responde(mensagem)
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(f"🏥 *SaúdeBot Moçambique*\n\n{resposta_ia}\n\n⚠️ Consulta sempre um médico!")
    return str(resp)

@app.route('/', methods=['GET'])
def home():
    return "🏥 SaúdeBot Moçambique está online! 🇲🇿"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
