import requests
import json
from django.conf import settings

class GoogleAgendaService:
    @staticmethod
    def enviar_para_google(sala, titulo, data_inicio, data_fim, email_cliente):
        """
        Faz a ponte com o Google Apps Script para criar o evento na agenda.
        """
        url = "https://script.google.com/macros/s/AKfycbymv1RJ7XNXTsyt39Q1DvC2DKdxdMayacOrQJFenXdy_CygFs1jMbHkzxgEr2ca0jh8/exec"
        
        # Mapeamento das salas para as variáveis do settings.py
        # A equipe precisa configurar ID_SALA_A e ID_SALA_B no settings/env
        calendar_id = settings.ID_SALA_A if sala == 'A' else settings.ID_SALA_B

        payload = {
            "token": settings.APPS_SCRIPT_TOKEN, # Chave de segurança definida no seu .env
            "calendar_id": calendar_id,
            "titulo": titulo,
            "inicio": data_inicio, # Espera string no formato ISO (YYYY-MM-DDTHH:MM:SS)
            "fim": data_fim,
            "email_cliente": email_cliente
        }

        try:
            # Timeout de 15 segundos porque APIs de terceiros podem demorar a responder
            response = requests.post(url, data=json.dumps(payload), timeout=15)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "erro", "message": f"Falha na conexão com o servidor Google: {str(e)}"}