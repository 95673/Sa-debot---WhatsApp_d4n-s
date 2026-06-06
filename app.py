from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

app = Flask(__name__)

CHAVE_GROQ = os.environ.get("CHAVE_GROQ")

PERSONALIDADE_WHATSAPP = """
És o SaúdeBot, assistente de saúde virtual para Moçambique.
Respondes SEMPRE em português de Moçambique.
Respostas curtas e claras — máximo 3 parágrafos.
Sugeres sempre consultar um médico para casos graves.
"""

def groq_responde(mensagem, curto=False):
    sistema = "SaúdeBot Moçambique. Responde em português. Máximo 160 caracteres." if curto else PERSONALIDADE_WHATSAPP
    resposta = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {CHAVE_GROQ}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": mensagem}
            ],
            "max_tokens": 100 if curto else 300
        }
    )
    dados = resposta.json()
    if "choices" in dados:
        return dados["choices"][0]["message"]["content"]
    return "Erro na ligacao."

# ===== WHATSAPP =====
@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    mensagem = request.form.get('Body', '')
    numero = request.form.get('From', '')
    print(f"WhatsApp de {numero}: {mensagem}")
    resposta_ia = groq_responde(mensagem)
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(f"🏥 *SaúdeBot Moçambique*\n\n{resposta_ia}\n\n⚠️ Consulta sempre um médico!")
    return str(resp)

# ===== USSD =====
@app.route('/ussd', methods=['POST'])
def ussd():
    text = request.form.get('text', '')
    if text == '':
        return "CON Bem-vindo ao SaudeBot\nMocambique\n1. Sintomas\n2. Hospitais\n3. Emergencias\n4. Medicamentos\n5. Falar com IA"
    elif text == '1':
        return "CON Selecciona o sintoma:\n1. Malaria\n2. Colera\n3. Diabetes\n4. AVC\n5. Gastrite\n6. HIV e SIDA"
    elif text == '1*1':
        return "END " + groq_responde("Sintomas da malaria em 2 frases.", curto=True)
    elif text == '1*2':
        return "END " + groq_responde("Sintomas da colera em 2 frases.", curto=True)
    elif text == '1*3':
        return "END " + groq_responde("Sintomas da diabetes em 2 frases.", curto=True)
    elif text == '1*4':
        return "END " + groq_responde("Sintomas do AVC em 2 frases.", curto=True)
    elif text == '1*5':
        return "END " + groq_responde("Sintomas da gastrite em 2 frases.", curto=True)
    elif text == '1*6':
        return "END " + groq_responde("Sintomas do HIV e SIDA em 2 frases.", curto=True)
    elif text == '2':
        return "END Hospitais:\n-Central: 21 320 000\n-Mavalane: 21 470 000\n-Matola: 21 720 000\n-CUF: 21 350 000"
    elif text == '3':
        return "END Emergencias:\nBombeiros: 119/112\nPolicia: 119\nINEM: 192\nEDM: 1455\nMISAU: 110\nSaude: 1490"
    elif text == '4':
        return "CON Medicamentos:\n1. Febre e Dor\n2. Diarreia\n3. Malaria\n4. Infeccoes"
    elif text == '4*1':
        return "END Paracetamol 500mg\nou Ibuprofeno 400mg\ncada 8 horas.\nConsulta um medico!"
    elif text == '4*2':
        return "END Sais de Reidratacao\n1 saqueta em 1L agua.\nBeba devagar."
    elif text == '4*3':
        return "END Artesunato ou\nCloroquina\nconforme prescricao."
    elif text == '4*4':
        return "END Amoxicilina 500mg\nou Metronidazol 400mg\nconforme prescricao."
    elif text == '5':
        return "END SaudeBot completo:\nhuggingface.co/spaces/\nBernardo24/26052026"
    else:
        return "END Opcao invalida.\nMarca *384*18442#\npara recomecar."

@app.route('/', methods=['GET'])
def home():
    return "SaudeBot Mocambique — WhatsApp + USSD online! 🇲🇿"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
