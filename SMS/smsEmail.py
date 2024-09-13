import smtplib
from email.mime.text import MIMEText

# Configuração do servidor SMTP
smtp_server = 'smtp.gmail.com'
smtp_port = 587
username = 'nktcpny@gmail.com'
password = 'bhashjgujjayunen'

# Criação do e-mail
msg = MIMEText('conteudo')
msg['Subject'] = 'tema'
msg['From'] = 'nktcpny@gmail.com'
msg['To'] = 'matheus.mattos4237@gmail.com'

# Envio do e-mail
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Inicializa a conexão segura
        server.login(username, password)  # Realiza o login
        server.sendmail(msg['From'], msg['To'], msg.as_string())  # Envia a mensagem
        print('E-mail enviado com sucesso!')
except Exception as e:
    print(f'Ocorreu um erro ao enviar o e-mail: {e}')
