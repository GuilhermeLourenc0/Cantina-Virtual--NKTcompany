# import random
# from twilio.rest import Client
# from flask import Flask, request, render_template

# app = Flask(__name__)

# # Suas credenciais Twilio
# account_sid = 'AC475dc4dd74f017977d282babb6ed02fe'
# auth_token = '54f807df630fa436c0b2820b5482939f'

# # Crie um client
# client = Client(account_sid, auth_token)

# # Phone number to send the verification code to
# user_phone_number = "+5516992360708"

# # Gerar um código de verificação aleatório com 4 dígitos, incluindo zeros à esquerda
# verification_code = str(random.randint(90, 9999)).zfill(4)

# # Armazenar o código de verificação (opcional)
# verification_codes = {}
# verification_codes[user_phone_number] = verification_code

# # Enviar o código de verificação via SMS
# message = client.messages.create(
#     to=user_phone_number,
#     from_="+13195190041",
#     body=f'Seu código é: {verification_code}'
# )
# print(message.sid)

# # Rota para a página de verificação
# @app.route('/verificacao', methods=['GET', 'POST'])
# def verificacao():
#     erro = None
#     if request.method == 'POST':
#         user_input_code = request.form['codigo']
#         if user_input_code == verification_codes.get(user_phone_number):
#             return 'Código de verificação correto!'
#         else:
#             erro = 'Código de verificação incorreto. Tente novamente!'
#     return render_template('verificacao.html', erro=erro)

# if __name__ == '__main__':
#     app.run(debug=True)