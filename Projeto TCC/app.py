from flask import Flask, render_template, request, redirect, session, jsonify, flash, Response, url_for
from usuario import Usuario
from sistema import Sistema
from carrinho import Carrinho
from perfil import Perfil
from adm import Adm
import random
from twilio.rest import Client
import os
from datetime import datetime
import pytz
from relatorio import Relatorio


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Chave secreta para gerenciamento de sessões


# Configuração do diretório de upload
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

# Crie o diretório se ele não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



account_sid = 'AC475dc4dd74f017977d282babb6ed02fe'
auth_token = '54f807df630fa436c0b2820b5482939f'

# Crie um client
client = Client(account_sid, auth_token)



def verificar_sessao():
    """
    Função genérica para verificar o estado da sessão do usuário.
    Se o usuário estiver no meio do processo de verificação incompleta,
    a sessão será limpa.
    """
    if 'usuario_logado' in session and session.get('verificacao_incompleta'):
        # Limpa a sessão de usuário e a flag de verificação incompleta
        session.pop('usuario_logado', None)
        session.pop('verificacao_incompleta', None)



@app.route("/")
def principal():
    try:
        verificar_sessao()

        # Redirecionar para a página inicial do administrador se o tipo for 'adm'
        if 'usuario_logado' in session and session['usuario_logado'].get('tipo') == 'adm':
            return redirect("/inicialadm")

        # Verifica se o site está aberto, sem a necessidade de login
        timezone_sp = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(timezone_sp)
        hora_atual = now.hour
        minutos_atuais = now.minute
        site_aberto = hora_atual >= 7 and (hora_atual < 21 or (hora_atual == 21 and minutos_atuais < 45))

        # Obter o status de login bem-sucedido para exibir o alerta
        success = session.pop('login_sucesso', False)

        if site_aberto:
            sistema = Sistema()
            produtos_por_categoria = sistema.exibir_produtos()
            lista_marmitas = sistema.exibir_marmitas()
            return render_template(
                "index.html",
                produtos_por_categoria=produtos_por_categoria,
                lista_marmitas=lista_marmitas,
                site_aberto=site_aberto,
                success=success,
            )

        return render_template("index.html", site_aberto=site_aberto, success=success)

    except Exception as e:
        print(f"Erro ao verificar o horário de funcionamento: {e}")
        return "Erro ao verificar o horário de funcionamento."







@app.route("/produtos_json", methods=['GET'])
def produtos():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    produtos_por_categoria = sistema.exibir_produtos()  # Obtém a lista de produtos agrupados
    
    # Cria uma lista para armazenar todos os produtos com a categoria associada
    lista_produtos = []
    
    # Itera sobre as categorias e adiciona os produtos à lista
    for categoria in produtos_por_categoria.values():
        for produto in categoria['produtos']:
            produto_com_categoria = {
                'id_produto': produto['id_produto'],
                'nome_produto': produto['nome_produto'],
                'preco': produto['preco'],
                'imagem_produto': produto['imagem_produto'],
                'descricao': produto['descricao'],
                'nome_categoria': categoria['nome_categoria']  # Inclui o nome da categoria
            }
            lista_produtos.append(produto_com_categoria)

    return jsonify(lista_produtos)  # Retorna a lista de produtos em formato JSON




@app.route("/marmitas_json", methods=['GET'])
def marmitas():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_marmitas = sistema.exibir_marmitas()  # Obtém a lista de produtos
    return jsonify(lista_marmitas)  # Retorna os produtos em formato JSON



@app.route("/inicialadm")
def inicialadm():
    # Verifica e limpa a sessão se necessário
    verificar_sessao()
    # Verifica se o usuário está logado e possui um ID de cliente válido
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    
    # Verifica se o tipo do usuário é 'adm'
    if session['usuario_logado']['tipo'] == "cliente":
        return redirect("/")  # Redireciona para a rota "/"
    
    # Renderiza a página inicialAdm.html se o usuário não for 'adm'
    return render_template("inicialAdm.html")




@app.route("/adm")
def principal_adm():
    # Verifica e limpa a sessão se necessário
    verificar_sessao()
    # Verifica se o usuário está logado e possui um ID de cliente válido
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    
    # Verifica se o tipo do usuário é 'adm'
    if session['usuario_logado']['tipo'] == "cliente":
        return redirect("/")  # Redireciona para a rota "/"
    
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos_adm()  # Obtém a lista de produtos
    lista_marmitas = sistema.exibir_marmitas_adm()
    return render_template("index-adm.html", lista_produtos=lista_produtos, lista_marmitas = lista_marmitas)  # Renderiza a página inicial com a lista de produtos

# Rota de cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    # Redireciona para "/" se o usuário já estiver logado
    if 'usuario_logado' in session:
        return redirect("/")

    if request.method == 'GET':
        verificar_sessao()
        usuario = Usuario()
        cursos = usuario.exibir_cursos()
        return render_template("cadastrar.html", cursos=cursos)
    else:
        # Recebe os dados do formulário
        nome = request.form["nome"]
        telefone = request.form["tel"]
        email = request.form["email"]
        senha = request.form["senha"]
        curso = request.form["curso"]
        tipo = "cliente"

        usuario = Usuario()

        # Verifica se o email ou telefone já estão cadastrados
        if usuario.verificar_duplicidade(email, telefone):
            flash("Email ou telefone já cadastrado.")
            return redirect("/cadastro")

        # Gera o código de verificação e o envia
        verification_code = str(random.randint(1000, 9999)).zfill(4)
        message = client.messages.create(
            to=telefone,
            from_="+13195190041",
            body=f'Seu código é: {verification_code}'
        )
        print(message.sid)

        # Armazena dados temporários na sessão para realizar o cadastro após a verificação
        session['dados_cadastro'] = {
            "nome": nome,
            "telefone": telefone,
            "email": email,
            "senha": senha,
            "curso": curso,
            "tipo": tipo,
            "verification_code": verification_code
        }
        session['tipo_verificacao'] = "cadastro"  # Define o tipo de verificação como cadastro

        # Redireciona para a página de verificação
        return redirect("/verificacao")


@app.route("/verificacao", methods=["GET", "POST"])
def verificacao():
    if 'dados_cadastro' not in session and 'email_pendente' not in session:
        # Redireciona para login se faltar informações
        session.pop('usuario_logado', None)
        return redirect("/logar")

    if request.method == 'GET':
        return render_template("verificacao.html")

    # Código inserido pelo usuário
    codigo_inserido = "".join([request.form["codigo1"], 
                               request.form["codigo2"], 
                               request.form["codigo3"], 
                               request.form["codigo4"]])
    verification_code = session.get('verification_code')
    tipo_verificacao = session.get('tipo_verificacao')

    if codigo_inserido == verification_code:
        # Verificação bem-sucedida
        if tipo_verificacao == "cadastro":
            dados_cadastro = session.pop('dados_cadastro', None)
            if dados_cadastro:
                usuario = Usuario()
                usuario.cadastrar(
                    dados_cadastro["nome"],
                    dados_cadastro["telefone"],
                    dados_cadastro["email"],
                    dados_cadastro["senha"],
                    dados_cadastro["curso"],
                    dados_cadastro["tipo"]
                )

                # Login automático após o cadastro
                usuario.logar(dados_cadastro["email"], dados_cadastro["senha"])
                if usuario.logado:
                    session['usuario_logado'] = {
                        "nome": usuario.nome, 
                        "email": usuario.email, 
                        "tel": usuario.tel, 
                        "id_cliente": usuario.id_cliente, 
                        "tipo": usuario.tipo
                    }
            session.pop('verification_code', None)
            session.pop('tipo_verificacao', None)
            return redirect("/")

        elif tipo_verificacao == "atualizar_dados_iniciais":
            id_cliente = session['usuario_logado']['id_cliente']
            telefone = session['telefone']
            email = session.pop('email_pendente')
            senha = session.pop('senha_pendente')

            # Atualiza o telefone
            usuario = Usuario()
            usuario.atualizar_telefone(id_cliente, telefone)  # Atualiza o telefone no banco

            # Agora atualiza os dados (email e senha)
            usuario.atualizar_dados(id_cliente, telefone, email, senha)  # Atualiza o email e senha, mas telefone já foi atualizado

            session.pop('verification_code', None)
            session.pop('tipo_verificacao', None)
            session.pop('verificacao_incompleta', None)

            return redirect("/inicialadm")


    else:
        return render_template("verificacao.html", erro="Código incorreto. Tente novamente.")









@app.route("/logar", methods=['GET', 'POST'])
def logar():
    if request.method == 'GET':
        # Verifica se o usuário já está logado
        if 'usuario_logado' in session:
            usuario = session['usuario_logado']
            # Redireciona conforme o tipo do usuário
            if usuario.get('tipo') == 'adm':
                return redirect("/inicialadm")
            else:
                return redirect("/")
            
        
        # Renderiza a página de login para usuários não logados
        erro = session.pop('login_erro', False)
        return render_template('login.html', success=False, erro=erro)
    
    # Processa o formulário de login
    senha = request.form['senha']
    email = request.form['email']
    usuario = Usuario()
    usuario.logar(email, senha)
    
    if usuario.logado:
        # Define os dados do usuário na sessão
        session['usuario_logado'] = {
            "nome": usuario.nome, 
            "email": usuario.email, 
            "tel": usuario.tel, 
            "id_cliente": usuario.id_cliente, 
            "tipo": usuario.tipo,
            "senha": usuario.senha,
            "primeiro_login": usuario.primeiro_login
        }
        
        print("Sessão após login:", session)  # Verificação de sessão
        
        # Redireciona com base no tipo e status do login
        if usuario.tipo != 'cliente' and not usuario.primeiro_login:
            return redirect("/inicialadm")
        
        if usuario.tipo != 'cliente' and usuario.primeiro_login:
            session['verificacao_incompleta'] = True  # Marca a sessão para verificação incompleta
            return redirect("/atualizar_dados_iniciais")  # Redireciona para a atualização de dados
        
        session['login_sucesso'] = True
        return redirect("/")
    
    # Define erro de login na sessão e redireciona para login
    session['login_erro'] = True
    return redirect("/logar")




@app.route("/atualizar_dados_iniciais", methods=["GET", "POST"])
def atualizar_dados_iniciais():
    # Verifica se o usuário está logado e se a verificação está pendente
    if 'usuario_logado' not in session:
        return redirect("/logar")
    
    if not session.get('verificacao_incompleta'):
        return redirect("/")
    
    if request.method == 'GET':
        return render_template("atualizar_dados_iniciais.html")

    # Processa a atualização dos dados
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not telefone or not email or not senha:
        return render_template("atualizar_dados_iniciais.html", erro="Preencha todos os campos.")

    id_cliente = session['usuario_logado']['id_cliente']
    usuario = Usuario()
    usuario.atualizar_telefone(id_cliente, telefone)

    # Salva os dados pendentes na sessão
    session['telefone'] = telefone
    session['email_pendente'] = email
    session['senha_pendente'] = senha
    session['verification_code'] = str(random.randint(1000, 9999)).zfill(4)
    session['tipo_verificacao'] = "atualizar_dados_iniciais"

    # Envia o código de verificação
    message = client.messages.create(
        to=telefone,
        from_="+13195190041",
        body=f'Seu código é: {session["verification_code"]}'
    )
    session['verificacao_incompleta'] = True
    return redirect("/verificacao")
















# Rota para logout de usuários
@app.route('/logout')
def logout():
    if request.method == 'GET':
        id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão
        usuario = Usuario()  # Cria uma instância da classe Usuario
        usuario.logout(id_cliente)  # Realiza o logout do usuário
        session.clear()  # Limpa a sessão
        return redirect("/")  # Redireciona para a página inicial


@app.route('/inserir_produtos', methods=['POST'])
def inserir_produtos():
    # Verifica se o usuário está logado e possui um ID de cliente válido
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    
    # Verifica se o tipo do usuário é 'adm'
    if session['usuario_logado']['tipo'] == "cliente":
        return redirect("/")  # Redireciona para a rota "/"
    nome = request.form['nome']
    preco = request.form['preco']
    img = request.form['img']
    descricao = request.form['descricao']
    categoria = request.form['categoria']
    
    # Captura o tamanho da marmita (campo exibido apenas quando marmita for selecionada)
    tamanho = request.form.get('tamanho')

    # Captura as guarnições existentes (selecionadas via checkbox)
    guarnicoes_existentes = request.form.getlist('guarnicoes')

    # Captura os acompanhamentos existentes (selecionados via checkbox)
    acompanhamentos_existentes = request.form.getlist('acompanhamentos')

    # Captura as novas guarnições
    novas_guarnicoes = request.form.getlist('nova_guarnicoes')

    # Cria uma instância do objeto que contém o método de inserção
    adm = Adm()  # Substitua pelo seu objeto real

    # Verifica se a categoria selecionada é "Marmita"
    id_categoria_marmita = 7  # Substitua pelo ID real da categoria "Marmita"
    
    if int(categoria) == id_categoria_marmita:
        # Insere uma marmita e associa guarnições e acompanhamentos
        sucesso = adm.inserir_marmita(nome, preco, img, descricao, tamanho, guarnicoes_existentes, novas_guarnicoes, acompanhamentos_existentes)
    else:
        # Insere um produto normal
        sucesso = adm.inserir_produto(nome, preco, img, descricao, categoria, novas_guarnicoes)

    return redirect('/inicialadm')  # Redireciona para a página inicial ou outra página desejada







@app.route("/exibir_guarnicao")
def exibir_guarnicao():
    # Verifica se o usuário está logado e possui um ID de cliente válido
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    
    # Verifica se o tipo do usuário é 'adm'
    if session['usuario_logado']['tipo'] == "cliente":
        return redirect("/")  # Redireciona para a rota "/"
    adm = Adm()
    lista_guarnicao = adm.exibir_guarnicao()
    lista_acompanhamento = adm.exibir_acompanhamento()
    categorias = adm.exibir_categorias()
    return render_template("cad-produto.html", lista_guarnicao=lista_guarnicao, lista_acompanhamento=lista_acompanhamento, categorias=categorias)



@app.route('/adicionar_guarnicao', methods=['POST'])
def adicionar_guarnicao():
    nome_guarnicao = request.form.get('nome_guarnicao')
    adm = Adm()
    if nome_guarnicao:
        sucesso, id_guarnicao = adm.inserir_guarnicao(nome_guarnicao)  # Modifique a função para retornar o ID
        return jsonify(success=sucesso, id_guarnicao=id_guarnicao)
    return jsonify(success=False)
 




@app.route('/adicionar_acompanhamento', methods=['POST'])
def adicionar_acompanhamento():
    nome_acompanhamento = request.form.get('nome_acompanhamento')
    adm = Adm()
    if nome_acompanhamento:
        sucesso, id_acompanhamento = adm.inserir_acompanhamento(nome_acompanhamento)
        return jsonify(success=sucesso, id_acompanhamento=id_acompanhamento)
    return jsonify(success=False)





# Rota para exibição de produtos
@app.route("/exibir_produtos")
def compras():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos()  # Obtém a lista de produtos
    return render_template("produto.html", lista_produtos=lista_produtos)  # Renderiza a página com a lista de produtos


# Rota para exibir detalhes de um produto único
@app.route("/produto_unico", methods=['GET', 'POST'])
def exibir_produto_unico():
    
    if request.method == 'POST':
        btn_produto = request.form.get('btn-produto')  # Obtém o ID do produto selecionado
        session['id'] = {'id_produto': btn_produto}  # Armazena o ID na sessão
        
    # Recupera o ID do produto da sessão
    id_produto = session['id'].get('id_produto')
    
    if id_produto is None:
        flash('ID do produto não encontrado.', 'error')
        return redirect('/')  # Redireciona se o ID não estiver na sessão

    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_prounico = sistema.exibir_produto(id_produto)
    
    if lista_prounico is None:
        flash('Produto não encontrado.', 'error')
        return redirect('/')  # Ou outra página que faça sentido

    # Renderiza o template com os detalhes do produto
    return render_template("produto.html", lista_prounico=lista_prounico)


# Rota para exibir detalhes de um produto único
@app.route("/marmita_unica", methods=['GET', 'POST'])
def exibir_marmita_unica():
    
    if request.method == 'POST':
        btn_marmita = request.form.get('btn-produto')  # Obtém o ID do produto selecionado
        session['id'] = {'id_marmita': btn_marmita}  # Armazena o ID na sessão
        
    # Recupera o ID do produto da sessão
    id_marmita = session['id'].get('id_marmita')
    
    if id_marmita is None:
        flash('ID do produto não encontrado.', 'error')
        return redirect('/')  # Redireciona se o ID não estiver na sessão

    sistema = Sistema()  # Cria uma instância da classe Sistema
    dados_marmita = sistema.exibir_marmita(id_marmita)  # Aqui agora retorna um único item
    
    if dados_marmita is None:
        flash('Produto não encontrado.', 'error')
        return redirect('/')  # Ou outra página que faça sentido

    # Renderiza o template com os detalhes do produto
    return render_template("marmita.html", marmita=dados_marmita[0])



# Habilitar e desabilitar o produto (adm)
@app.route("/desabilitar_produto_adm", methods=['POST'])
def desabilitar_produto_adm():
    try:
        adm = Adm()  # Cria uma instância da classe Sistema
        btn_desabilitar = request.form.get("btn_desabilitar")  # Obtém o ID do produto
        adm.desabilitar_produto_adm(btn_desabilitar)  # Desabilita o produto
        return jsonify({'status': 'success'})  # Retorna uma resposta de sucesso
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500  # Retorna erro se algo falhar


@app.route("/habilitar_produto_adm", methods=['POST'])
def habilitar_produto_adm():
    try:
        adm = Adm()  # Cria uma instância da classe Sistema
        btn_habilitar = request.form.get("btn_habilitar")  # Obtém o ID do produto
        adm.habilitar_produto_adm(btn_habilitar)  # Habilita o produto
        return jsonify({'status': 'success'})  # Retorna uma resposta de sucesso
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500  # Retorna erro se algo falhar





# Habilitar e desabilitar marmita (adm)
@app.route("/desabilitar_marmita_adm", methods=['POST'])
def desabilitar_marmita_adm():
    try:
        adm = Adm()  # Cria uma instância da classe Sistema
        btn_desabilitar = request.form.get("btn_desabilitar")  # Obtém o ID da marmita
        adm.desabilitar_marmita_adm(btn_desabilitar)  # Desabilita a marmita
        return jsonify({'status': 'success'})  # Retorna uma resposta de sucesso
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500  # Retorna erro se algo falhar


@app.route("/habilitar_marmita_adm", methods=['POST'])
def habilitar_marmita_adm():
    try:
        adm = Adm()  # Cria uma instância da classe Sistema
        btn_habilitar = request.form.get("btn_habilitar")  # Obtém o ID da marmita
        adm.habilitar_marmita_adm(btn_habilitar)  # Habilita a marmita
        return jsonify({'status': 'success'})  # Retorna uma resposta de sucesso
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500  # Retorna erro se algo falhar






# ========== Pedidos ==========

@app.route("/exibir_pedidos", methods=['GET'])
def exibir_pedidos_route():
    # Verifica se o usuário está logado e possui um ID de cliente válido
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    
    # Verifica se o tipo do usuário é 'adm'
    if session['usuario_logado']['tipo'] == "cliente":
        return redirect("/")  # Redireciona para a rota "/"

    try:
        adm = Adm()  # Cria uma instância da classe Adm
        lista_pedidos = adm.exibir_pedidos()  # Obtém a lista de pedidos
        return render_template('recebePedido.html', lista_pedidos=lista_pedidos)  # Passa a variável para o template

    except Exception as e:
        print(f"Erro ao exibir pedidos: {e}")  # Log do erro
        return render_template('error.html', message="Erro ao carregar pedidos.")  # Renderiza uma página de erro



@app.route("/obter_pedidos", methods=['GET'])
def obter_pedidos():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona se não estiver logado

    try:
        adm = Adm()  # Cria uma instância da classe Adm
        lista_pedidos = adm.exibir_pedidos()  # Obtém a lista de pedidos
        print(lista_pedidos)  # Debug: Verifique os dados retornados
        return jsonify(lista_pedidos)  # Retorna a lista de pedidos em formato JSON

    except Exception as e:
        print(f"Erro ao obter pedidos: {e}")  # Log do erro
        return jsonify({'error': "Erro ao carregar pedidos."})  # Retorna mensagem de erro em JSON






@app.route('/marcar_entregue/<int:id_pedido>', methods=['POST'])
def marcar_entregue(id_pedido):
    try:
        adm = Adm()  # Cria uma instância da classe Adm
        adm.atualizar_status_pedido_entregue(id_pedido)  # Chama a função para atualizar o status
        return jsonify({'status': 'sucesso'})  # Retorna sucesso em JSON
    
    except Exception as e:
        print(f"Erro ao marcar pedido como entregue: {e}")  # Log do erro
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500  # Retorna mensagem de erro em JSON









# Rota para atualizar o status do pedido
@app.route("/atualizar_status_pedido", methods=['POST'])
def atualizar_status_pedido():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona se não estiver logado

    # Obtém o ID do pedido e o novo status enviados pelo AJAX
    id_pedido = request.form.get('id_pedido')
    novo_status = request.form.get('status')

    # Verifica se o ID do pedido e o status são válidos
    if id_pedido and novo_status:
        sistema = Sistema()  # Cria uma instância da classe Sistema
        sucesso = sistema.atualizar_status_pedido(id_pedido, novo_status)  # Atualiza o status do pedido no sistema
        
        if sucesso:
            return jsonify({'status': 'sucesso'})
        else:
            return jsonify({'status': 'erro', 'mensagem': 'Não foi possível atualizar o status.'})
    return jsonify({'status': 'erro', 'mensagem': 'Dados inválidos.'})


@app.route("/cancelar_pedido", methods=['POST'])
def cancelar_pedido():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona se não estiver logado

    id_pedido = request.form.get('id_pedido')
    motivo_cancelamento = request.form.get('motivo_cancelamento')  # Obtém o motivo do cancelamento (select)
    descricao_cancelamento = request.form.get('descricao_cancelamento')  # Obtém a descrição do cancelamento (textarea)

    # Verifica se o ID do pedido e pelo menos um motivo ou descrição do cancelamento foram fornecidos
    if id_pedido and (motivo_cancelamento or descricao_cancelamento):
        sistema = Sistema()  # Cria uma instância da classe Sistema
        motivo_final = motivo_cancelamento if motivo_cancelamento else descricao_cancelamento  # Usa o motivo ou a descrição
        sucesso = sistema.cancelar_pedido(id_pedido, motivo_final)  # Passa o motivo para a função

        if sucesso:
            return jsonify({'status': 'sucesso'})
        else:
            return jsonify({'status': 'erro', 'mensagem': 'Não foi possível cancelar o pedido.'})
    return jsonify({'status': 'erro', 'mensagem': 'Dados inválidos.'})





@app.route("/enviar_carrinho", methods=['POST'])
def enviar_carrinho():
    try:
        timezone_sp = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(timezone_sp)
        hora_atual = now.strftime("%H:%M:%S")  # Captura a hora atual no formato HH:MM:SS
        print(f"Hora atual: {hora_atual}")

        # Verifica se está dentro do horário de funcionamento (entre 7h00 e 21h45)
        site_aberto = (now.hour > 7 or (now.hour == 7 and now.minute >= 0)) and (now.hour < 21 or (now.hour == 21 and now.minute <= 45))

        if not site_aberto:
            return jsonify({"error": "Site offline. Não é possível enviar pedidos neste horário."}), 403

        if 'usuario_logado' in session:
            id_cliente = session['usuario_logado']['id_cliente']
            data = request.get_json()

            # Verifica se os dados foram enviados corretamente
            if data is None:
                return jsonify(success=False, message="Erro ao obter dados do carrinho."), 400

            itens = data.get('itens', [])
            
            # Verifica se os itens estão vazios
            if not itens:
                return jsonify(success=False, message="Carrinho está vazio."), 400

            try:
                carrinho = Carrinho()
                if carrinho.enviar_carrinho(id_cliente, itens, hora_atual):  # Passa a hora atual
                    # Chama a função para remover todo o carrinho
                    carrinho.remover_todo_carrinho(id_cliente)
                    return jsonify(success=True, message="Pedido enviado com sucesso!", redirect="/exibir_pedidos")
                else:
                    return jsonify(success=False, message="Erro ao enviar o carrinho."), 500
            except Exception as e:
                print(f"Erro ao processar pedido: {e}")
                return jsonify(success=False, message="Erro interno do servidor."), 500
                
        return jsonify(success=False, message="Usuário não autenticado."), 401

    except Exception as e:
        print(f"Erro ao obter horário de Brasília: {e}")
        return jsonify({"error": "Erro ao verificar o horário de funcionamento."}), 500













# ========== Histórico de Pedidos ==========
@app.route("/historico", methods=['GET'])
def historico():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    else:
        return render_template('historico.html')  # Carrega o template da página de histórico


@app.route("/exibir_historico_ajax", methods=['GET'])
def exibir_historico_ajax():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona para a página de login via JSON
    else:
        id_cliente = session['usuario_logado']['id_cliente']
        sistema = Sistema()  # Cria uma instância da classe Sistema
        lista_historico = sistema.exibir_historico(id_cliente)  # Obtém a lista de pedidos

        return jsonify(lista_historico)  # Retorna os pedidos como JSON


# ========== Carrinho ==========
    
# Rota para atualizar o preço total do carrinho via AJAX
@app.route("/atualizar_preco_total", methods=['GET'])
def atualizar_preco_total():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    id_cliente = session.get('usuario_logado')['id_cliente']

    try:
        carrinho = Carrinho()
        lista_carrinho = carrinho.exibir_carrinho(id_cliente)
        return jsonify({'success': True, 'total_preco': lista_carrinho['total_preco']})

    except Exception as e:
        print(f"Erro ao atualizar preço total: {e}")
        return jsonify({'success': False, 'message': 'Erro ao atualizar preço total'})
    

# Rota para atualizar a quantidade de um produto no carrinho via AJAX
@app.route("/atualizar_quantidade", methods=['POST'])
def atualizar_quantidade():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    id_cliente = session.get('usuario_logado')['id_cliente']

    try:
        data = request.get_json()
        id_carrinho = data.get('id_carrinho')
        quantidade = data.get('quantidade')

        if not id_carrinho or not quantidade:
            return jsonify({'success': False, 'message': 'Dados incompletos'})

        carrinho = Carrinho()
        carrinho.atualizar_quantidade_produto_carrinho(id_carrinho, quantidade)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Erro ao atualizar quantidade: {e}")
        return jsonify({'success': False, 'message': 'Erro ao atualizar quantidade'})
        

# Rota para excluir um item (produto ou marmita) do carrinho
@app.route("/excluir_produto_carrinho", methods=['POST'])
def excluir_produto_carrinho():
    # Verifica se o usuário está autenticado
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        # Obtém os dados JSON da requisição
        data = request.get_json()
        id_carrinho = data.get('id_carrinho')  # Obtém o ID do item no carrinho

        # Verifica se o ID do carrinho foi fornecido
        if not id_carrinho:
            return jsonify({'success': False, 'message': 'ID do carrinho não encontrado'})

        carrinho = Carrinho()  # Cria uma instância da classe Carrinho
        carrinho.remover_produto_carrinho(id_carrinho)  # Remove o item do carrinho

        return jsonify({'success': True})  # Retorna sucesso se a exclusão for bem-sucedida

    except Exception as e:
        print(f"Erro ao excluir item do carrinho: {e}")  # Registra o erro no console
        return jsonify({'success': False, 'message': 'Erro ao excluir item do carrinho'})

    

@app.route("/exibir_carrinho", methods=['GET', 'POST'])
def exibir_carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    else:
        carrinho = Carrinho()  # Cria uma instância da classe Carrinho
        id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão

        if request.method == 'POST':
            if 'btn-excluir' in request.form:
                id_carrinho = request.form['btn-excluir']
                carrinho.remover_produto_carrinho(id_carrinho)
            else:
                quantidades = request.form.getlist('quantidades')
                for id_carrinho, quantidade in quantidades.items():
                    carrinho.atualizar_quantidade_produto_carrinho(id_carrinho, quantidade)

        lista_carrinho = carrinho.exibir_carrinho(id_cliente)  # Obtém a lista de produtos no carrinho
        return render_template("carrinho.html", lista_carrinho=lista_carrinho)  # Renderiza a página do carrinho com a lista de produtos



    


@app.route("/inserir_carrinho", methods=['POST'])
def carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({"success": False, "error": "Usuário não logado."}), 401  # Código 401 para não autorizado

    id_cliente = session.get('usuario_logado')['id_cliente']
    cod_produto = request.form.get('cod_produto')  # Para produtos
    id_marmita = request.form.get('id_marmita')  # Para marmitas

    # Se for uma marmita, aplica a restrição de horário
    if id_marmita:
        # Obtém o horário atual de São Paulo
        timezone_sp = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(timezone_sp)
        hora_atual = now.hour
        minutos_atuais = now.minute
        print(f"Hora atual: {hora_atual}, Minutos atuais: {minutos_atuais}")

        # Verifica se o pedido é entre 7h e 15h30
        if (hora_atual < 7) or (hora_atual == 15 and minutos_atuais > 30) or (hora_atual > 15):
            return jsonify({"error": "Os pedidos de marmitas só podem ser feitos entre 7h e 15h30."}), 403

    # Captura guarnições e acompanhamentos selecionados
    guarnicoes_selecionadas = request.form.getlist('guarnicao')
    acompanhamentos_selecionados = request.form.getlist('acompanhamento')

    # Valida e insere no carrinho
    carrinho = Carrinho()
    if cod_produto or id_marmita:
        carrinho.inserir_item_carrinho(cod_produto, id_marmita, id_cliente, 
                                       guarnicoes_selecionadas, acompanhamentos_selecionados)

    # Envia uma resposta JSON com a URL de redirecionamento
    return jsonify({"success": True, "redirect_url": "/exibir_carrinho"})

















@app.route("/editar_produto", methods=['POST', 'GET'])
def editar_produto():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    
    if session['usuario_logado'].get('tipo') == 'cliente':
        return redirect('/')  # Redireciona clientes para a página inicial

    if request.method == 'POST':
        btn_produto = request.form.get('btn-produto')  # Obtém o ID do produto selecionado
        session['id'] = {'id_produto': btn_produto}  # Armazena o ID na sessão
        
    # Recupera o ID do produto da sessão
    id_produto = session['id'].get('id_produto')
    
    if id_produto is None:
        flash('ID do produto não encontrado.', 'error')
        return redirect('/')  # Redireciona se o ID não estiver na sessão

    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_prounico = sistema.exibir_produto(id_produto)
    
    if lista_prounico is None:
        flash('Produto não encontrado.', 'error')
        return redirect('/')  # Ou outra página que faça sentido

    # Renderiza o template com os detalhes do produto
    return render_template("editarProduto.html", lista_prounico=lista_prounico)


@app.route("/atualizar_produto", methods=['POST'])
def atualizar_produto():
    if 'usuario_logado' not in session:
        return redirect('/logar')

    if session['usuario_logado'].get('tipo') == 'cliente':
        return redirect('/')  # Redireciona clientes para a página inicial

    adm = Adm()  # Cria uma instância da classe Sistema
    id_produto = request.form.get('id_produto')
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    descricao = request.form.get('descricao')
    imagem = request.files.get('imagem')  # Para o upload de imagem

    # lógica para atualizar o produto no banco de dados
    adm.atualizar_produto(id_produto, nome, preco, descricao, imagem)

    flash('Produto atualizado com sucesso!', 'success')
    return redirect('/editar_produto')  # Ou para uma página de detalhes do produto


@app.route('/imagem_produto/<int:cod_produto>')
def imagem_produto(cod_produto):
    adm = Adm()  # Cria uma instância da classe Sistema
    imagem = adm.obter_imagem_produto(cod_produto)

    if imagem:
        return Response(imagem, mimetype='image/jpeg')  # Ajuste o tipo MIME conforme o tipo de imagem armazenado
    return "Imagem não encontrada", 404  # Retorna erro 404 se não encontrar a imagem







@app.route("/editar_marmita", methods=['POST', 'GET'])
def editar_marmita():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    
    if session['usuario_logado'].get('tipo') == 'cliente':
        return redirect('/')  # Redireciona clientes para a página inicial


    if request.method == 'POST':
        btn_marmita = request.form.get('btn-marmita')  # Obtém o ID do produto selecionado
        session['id'] = {'id_marmita': btn_marmita}  # Armazena o ID na sessão

    id_marmita = session['id'].get('id_marmita')
    
    if id_marmita is None:
        flash('ID da marmita não encontrado.', 'error')
        return redirect('/adm')  # Redireciona se o ID não estiver na sessão

    sistema = Sistema()  # Cria uma instância da classe
    lista_marunica = sistema.exibir_marmita(id_marmita)
    
    if not lista_marunica:
        flash('Nenhuma marmita encontrada.', 'error')
        return redirect('/inicialadm')  # Ou outra página relevante

    # Extrai os dados retornados, incluindo as guarnições e acompanhamentos
    marmita_dados = lista_marunica[0]
    
    # Renderiza o template com todos os dados necessários
    return render_template(
        "editarMarmita.html", 
        lista_marunica=lista_marunica,
        todos_acompanhamentos=marmita_dados['todos_acompanhamentos'],  # Passa todos os acompanhamentos
        todas_guarnicoes=marmita_dados['todas_guarnicoes']  # Passa todas as guarnições
    )







@app.route("/atualizar_marmita", methods=['POST'])
def atualizar_marmita():
    if 'usuario_logado' not in session:
        return jsonify({'status': 'error', 'message': 'Você precisa estar logado para realizar esta ação.'}), 401
    

    if session['usuario_logado'].get('tipo') == 'cliente':
        return redirect('/')  # Redireciona clientes para a página inicial
    
    adm = Adm()
    id_marmita = request.form['id_marmita']
    nome = request.form['nome']
    preco = request.form['preco']
    descricao = request.form['descricao']
    tamanho = request.form['tamanho']
    imagem = request.files.get('imagem')

    # Capturando acompanhamentos e guarnições selecionados
    acompanhamentos = request.form.getlist('acompanhamentos[]')
    guarnicoes = request.form.getlist('guarnicoes[]')

    # Validação dos campos obrigatórios
    if not id_marmita or not nome or not preco or not descricao or not tamanho:
        return jsonify({'status': 'error', 'message': 'Todos os campos obrigatórios devem ser preenchidos.'}), 400
    
    try:
        # Atualiza a marmita com os dados fornecidos
        adm.atualizar_marmita(id_marmita, nome, preco, descricao, tamanho, acompanhamentos, guarnicoes, imagem)
        return jsonify({'status': 'success', 'message': 'Marmita atualizada com sucesso!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Ocorreu um erro ao atualizar a marmita: {str(e)}'}), 500








@app.route('/imagem_marmita/<int:id_marmita>')
def imagem_marmita(id_marmita):
    adm = Adm()
    imagem = adm.obter_imagem_marmita(id_marmita)
    
    if imagem:
        return Response(imagem, mimetype='image/jpeg')  # Ajuste o tipo MIME conforme o tipo de imagem armazenado
    return "Imagem não encontrada", 404  # Retorna erro 404 se não encontrar a imagem








# Rota para solicitar troca de senha
@app.route("/trocar_senha", methods=['GET', 'POST'])
def trocar_senha():
    if request.method == 'GET':
        return render_template("trocar-senha.html")  # Renderiza a página para troca de senha
    else:
        email = request.form['email']
        telefone = request.form['telefone']
        
        # Verifique se o usuário existe (você deve implementar isso na classe Usuario)
        usuario = Usuario()
        if usuario.verificar_usuario(email, telefone):  # Supondo que exista uma função para verificar o usuário
            # Gerar um código de verificação aleatório com 4 dígitos, incluindo zeros à esquerda
            verification_code = str(random.randint(1000, 9999)).zfill(4)

            # Enviar o código de verificação via SMS
            message = client.messages.create(
                to=telefone,
                from_="+13195190041",
                body=f'Seu código para troca de senha é: {verification_code}'
            )
            print(message.sid)

            # Armazenar o telefone e o código de verificação na sessão
            session['telefone_verificacao'] = telefone
            session['verification_code'] = verification_code
            session['email_usuario'] = email  # Armazena o email do usuário na sessão
            
            return redirect("/verificacao_troca_senha")  # Redireciona para a tela de verificação
        else:
            flash("Usuário não encontrado. Verifique as informações.", "error")
            return redirect("/trocar_senha")


# Rota para verificação do código de troca de senha
@app.route("/verificacao_troca_senha", methods=['GET', 'POST'])
def verificacao_troca_senha():
    if request.method == 'GET':
        return render_template("verificacao-troca-senha.html")  # Renderiza a página onde o usuário insere o código
    else:
        codigo1 = request.form["codigo1"]
        codigo2 = request.form["codigo2"]
        codigo3 = request.form["codigo3"]
        codigo4 = request.form["codigo4"]
        codigo_inserido = codigo1 + codigo2 + codigo3 + codigo4
        verification_code = session.get('verification_code')

        if codigo_inserido == verification_code:
            return redirect("/nova_senha")  # Redireciona para a página para criar uma nova senha
        else:
            return render_template("verificacao-troca-senha.html", erro="Código incorreto. Tente novamente.")


# Rota para definir uma nova senha
@app.route("/nova_senha", methods=['GET', 'POST'])
def nova_senha():
    if request.method == 'GET':
        return render_template("nova-senha.html")  # Renderiza a página para inserir nova senha
    else:
        nova_senha = request.form['nova_senha']
        email_usuario = session.get('email_usuario')

        # Atualiza a senha do usuário (você deve implementar isso na classe Usuario)
        usuario = Usuario()
        if usuario.atualizar_senha(email_usuario, nova_senha):  # Implementar essa função na classe Usuario
            flash("Senha atualizada com sucesso!", "success")
            session.clear()  # Limpa a sessão após a troca de senha
            return redirect("/logar")  # Redireciona para a página de login
        else:
            flash("Erro ao atualizar a senha. Tente novamente.", "error")
            return redirect("/nova-senha")


# ================ PERFIL ================
@app.route('/perfil', methods=['GET'])
def perfil():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado

    # Recupera o ID do cliente da sessão
    id_cliente = session['usuario_logado'].get('id_cliente')
    
    perfil = Perfil()  # Cria uma instância da classe Sistema
    perfil_usuario = perfil.obter_perfil(id_cliente)  # Método que você deve criar para obter os detalhes do usuário
    
    if perfil_usuario is None:
        flash('Perfil não encontrado.', 'error')
        return redirect('/')  # Redireciona se o perfil não for encontrado

    # Renderiza o template com os detalhes do perfil
    return render_template("perfil.html", perfil_usuario=perfil_usuario)


@app.route('/atualizar_perfil', methods=['POST'])
def atualizar_perfil():
    if 'usuario_logado' not in session:
        return redirect('/logar')  # Redireciona se o usuário não estiver logado

    perfil = Perfil()  # Cria uma instância da classe Sistema

    # Obtém dados do formulário
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
    imagem_perfil = request.files.get('imagem_perfil')

    # Verifica se as senhas coincidem
    if senha != confirmar_senha:
        flash('As senhas não coincidem.', 'error')
        return redirect('/perfil')  # Redireciona para o perfil se houver erro

    # Obter o ID do cliente da sessão
    id_cliente = session['usuario_logado']['id_cliente']
    
    # Verifica a senha atual para confirmar a alteração
    if not perfil.verificar_senha(id_cliente, senha):
        flash('Senha incorreta.', 'error')
        return redirect('/perfil')

    # Verifica se uma imagem foi enviada
    caminho_imagem = None
    if imagem_perfil and imagem_perfil.filename != '':
        caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], imagem_perfil.filename)
        try:
            imagem_perfil.save(caminho_imagem)
            flash('Imagem salva com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao salvar a imagem: {str(e)}', 'error')
            return redirect('/perfil')  # Redireciona se falhar ao salvar a imagem

    # Atualiza nome e imagem (sem alterar a senha), verifica se o nome foi preenchido
    resultado = perfil.atualizar_perfil(id_cliente, nome if nome else None, caminho_imagem)

    if 'error' in resultado:
        flash(resultado['error'], 'error')
    else:
        flash('Perfil atualizado com sucesso!', 'success')

    return redirect('/perfil')  # Redireciona para a página de perfil após a atualização



@app.route('/imagem_perfil/<int:id_cliente>')
def imagem_perfil(id_cliente):
    perfil = Perfil()  # Cria uma instância da classe Sistema
    imagem = perfil.obter_imagem_perfil(id_cliente)

    if imagem:
        return Response(imagem, mimetype='image/jpeg')  # ou o tipo MIME correto para a imagem
    else:
        # Retorna a imagem padrão caso não exista imagem personalizada para o usuário
        return redirect(url_for('static', filename='img/default-avatar.png'))




@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio():
    # Verifica se o usuário está logado e possui um ID de cliente válido
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    
    # Verifica se o tipo do usuário é 'adm'
    if session['usuario_logado']['tipo'] == "cliente":
        return redirect("/")  # Redireciona para a rota "/"
    relatorio = Relatorio()
    relatorio_dados = []
    valor_total_geral = 0
    total_pedidos = 0
    cancelados_dados = []
    valor_total_cancelado = 0
    total_cancelados = 0

    if request.method == 'POST':
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        relatorio_dados, valor_total_geral, total_pedidos = relatorio.exibir_relatorio_entregue(data_inicial, data_final)
        cancelados_dados, valor_total_cancelado, total_cancelados = relatorio.exibir_relatorio_cancelado(data_inicial, data_final)

    return render_template("relatorio.html", 
                           relatorio_dados=relatorio_dados, 
                           valor_total_geral=valor_total_geral, 
                           total_pedidos=total_pedidos,
                           cancelados_dados=cancelados_dados,
                           valor_total_cancelado=valor_total_cancelado,
                           total_cancelados=total_cancelados)





@app.route('/usuario/<int:id_cliente>', methods=['GET'])
def usuario(id_cliente):
    if 'usuario_logado' not in session:
        return redirect('/logar')  # Redireciona se o usuário não estiver logado
    
    usuario = Usuario()  # Supondo que 'Usuario' seja uma classe que manipula os dados do cliente
    dados_cliente = usuario.tela_usuario(id_cliente)  # Método que retorna os dados do cliente
    pedidos_cliente = usuario.obter_pedidos(id_cliente)  # Método que retorna os pedidos do cliente
    
    # Adiciona a URL da imagem de perfil no contexto
    imagem_perfil_url = url_for('imagem_perfil', id_cliente=id_cliente)
    
    return render_template('usuario.html', cliente=dados_cliente, pedidos=pedidos_cliente, imagem_perfil_url=imagem_perfil_url)





app.run(debug=True, host="127.0.0.1", port=8080)  # Define o host como localhost e a porta como 8080