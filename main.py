import os
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
from datetime import datetime, timedelta, timezone  # Adicionar timezone

# Configurações de localização e e-mail
MY_LAT = 40.656586
MY_LONG = -7.912471

# Carregar credenciais de variáveis de ambiente para segurança
SERVER = "smtp.gmail.com"
PORT = 587
EMAIL_ADDRESS = "carlosmiguelromao@gmail.com"
PASSWORD = "fsem acem gxeq zxrq"

# Lista de destinatários de e-mail
EMAIL_RECIPIENTS = ["carlosmiguelromao@gmail.com", "bernardopintoromao2012@gmail.com"]

# Variáveis para reduzir a frequência das chamadas de API
last_sun_check = datetime.min
is_night_time = False


# Função para verificar a posição da ISS
def check_position():
    try:
        response_iss = requests.get("http://api.open-notify.org/iss-now.json")
        response_iss.raise_for_status()
        data_iss = response_iss.json()

        iss_latitude = float(data_iss["iss_position"]["latitude"])
        iss_longitude = float(data_iss["iss_position"]["longitude"])
        print(f"ISS position: {iss_latitude} | {iss_longitude}")

        # Verifica se a ISS está dentro de uma área de 5 graus de latitude e longitude
        if (MY_LAT - 5 <= iss_latitude <= MY_LAT + 5) and (MY_LONG - 5 <= iss_longitude <= MY_LONG + 5):
            return True
    except requests.RequestException as e:
        print(f"Erro ao obter posição da ISS: {e}")
    return False


# Função para verificar se é noite, com cache para reduzir chamadas à API
# Função para verificar se é noite, com cache para reduzir chamadas à API
def is_night():
    global last_sun_check, is_night_time
    if datetime.now() - last_sun_check > timedelta(hours=1):
        try:
            parameters = {
                "lat": MY_LAT,
                "lng": MY_LONG,
                "formatted": 0,
            }
            response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
            response.raise_for_status()
            data = response.json()

            sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
            sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

            # Atualizamos aqui para um objeto datetime com fuso horário UTC
            time_now = datetime.now(timezone.utc).hour
            is_night_time = time_now < sunrise or time_now > sunset
            last_sun_check = datetime.now()

        except requests.RequestException as e:
            print(f"Erro ao obter informações de nascer/pôr do sol: {e}")
    return is_night_time


# Loop principal de verificação e envio de e-mail
while True:
    try:
        # Se a ISS está próxima e é noite, envia um e-mail para todos os destinatários
        if check_position() and is_night():
            with smtplib.SMTP(SERVER, PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, PASSWORD)

                time_now = datetime.now()
                msg = MIMEText(f"Olha para cima!!!\n\n{time_now}", 'plain', 'utf-8')
                msg['Subject'] = Header("Estação Espacial Internacional a passar por Viseu!", 'utf-8')
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = ", ".join(EMAIL_RECIPIENTS)  # Definindo os destinatários no cabeçalho

                # Envia o e-mail para cada destinatário na lista
                for recipient in EMAIL_RECIPIENTS:
                    server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
                print(f"Email enviado para: {', '.join(EMAIL_RECIPIENTS)}")

    except smtplib.SMTPException as e:
        print(f"Erro ao enviar o e-mail: {e}")

    time.sleep(60)  # Pausa por 60 segundos
