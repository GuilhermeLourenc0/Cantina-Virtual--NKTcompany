# from flask import Flask, request, render_template, redirect, url_for, session
# import os
# import smtplib
# import random
# from email.mime.text import MIMEText

# app = Flask(__name__)
# app.secret_key = 'supersecretkey'

# def send_verification_email(to_email):
#     code = random.randint(100000, 999999)
#     subject = "Seu código de verificação"
#     body = f"Seu código de verificação é: {code}"
    
#     smtp_server = "smtp.gmail.com"
#     smtp_port = 587
#     smtp_user = os.getenv('EMAIL_USER')
#     smtp_password = os.getenv('EMAIL_PASS')
    
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = smtp_user
#     msg['To'] = to_email
    
#     with smtplib.SMTP(smtp_server, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_user, smtp_password)
#         server.send_message(msg)
    
#     return code

# @app.route('/send_code', methods=['GET', 'POST'])
# def send_code():
#     if request.method == 'POST':
#         email = request.form['email']
#         code = send_verification_email(email)
#         session['verification_code'] = code
#         return redirect(url_for('verify_code'))
#     return render_template('send_code.html')

# @app.route('/verify_code', methods=['GET', 'POST'])
# def verify_code():
#     if request.method == 'POST':
#         entered_code = request.form['code']
#         if entered_code == str(session.get('verification_code')):
#             return redirect(url_for('success'))
#         else:
#             return "Código inválido. Tente novamente."
#     return render_template('verify_code.html')

# @app.route('/success')
# def success():
#     return "Verificação bem-sucedida! Você pode agora acessar o site."

# if __name__ == '__main__':
#     app.run(debug=True)
