from flask import Flask, render_template, request, redirect, session, jsonify, flash, Response, url_for
from usuario import Usuario
from sistema import Sistema
from carrinho import Carrinho
from perfil import Perfil
from adm import Adm
import random
from twilio.rest import Client
import os




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


# Rota para a página inicial
@app.route("/")
def principal():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos()  # Obtém a lista de produtos
    lista_marmitas = sistema.exibir_marmitas()
    return render_template("index.html", lista_produtos=lista_produtos, lista_marmitas = lista_marmitas)  # Renderiza a página inicial com a lista de produtos


@app.route("/produtos_json", methods=['GET'])
def produtos():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos()  # Obtém a lista de produtos
    return jsonify(lista_produtos)  # Retorna os produtos em formato JSON


@app.route("/inicialadm")
def inicialadm():
    return render_template("inicialAdm.html") 


@app.route("/adm")
def principal_adm():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos_adm()  # Obtém a lista de produtos
    lista_marmitas = sistema.exibir_marmitas_adm()
    return render_template("index-adm.html", lista_produtos=lista_produtos, lista_marmitas = lista_marmitas)  # Renderiza a página inicial com a lista de produtos

# Define a rota de cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == 'GET':
        usuario = Usuario()
        cursos = usuario.exibir_cursos()
        return render_template("cadastrar.html", cursos=cursos)
    else:
        nome = request.form["nome"]
        telefone = request.form["tel"]
        email = request.form["email"]
        senha = request.form["senha"]
        curso = request.form["curso"]
        tipo = "cliente"

        usuario = Usuario()
        if usuario.cadastrar(nome, telefone, email, senha, curso, tipo):
            # Gerar um código de verificação aleatório com 4 dígitos, incluindo zeros à esquerda
            verification_code = str(random.randint(90, 9999)).zfill(4)

            # Enviar o código de verificação via SMS
            message = client.messages.create(
                to=telefone,
                from_="+13195190041",
                body=f'Seu código é: {verification_code}'
            )
            print(message.sid)

            # Armazenar o telefone e o código de verificação na sessão
            session['telefone_verificacao'] = telefone
            session['verification_code'] = verification_code
            usuario.logar(email, senha)
            if usuario.logado:
                # Se o login for bem-sucedido, armazena os dados do usuário na sessão
                session['usuario_logado'] = {
                    "nome": usuario.nome, 
                    "email": usuario.email, 
                    "tel": usuario.tel, 
                    "id_cliente": usuario.id_cliente, 
                    "tipo": usuario.tipo,
                    "senha": usuario.senha
                }
            # Redireciona para a tela de verificação
            return redirect("/verificacao")
        else:
            return redirect("/cadastro")


# Rota para a tela de verificação
@app.route("/verificacao", methods=["GET", "POST"])
def verificacao():
    if request.method == 'GET':
        return render_template("verificacao.html")  # Renderiza a página onde o usuário insere o código
    else:
        codigo1 = request.form["codigo1"]
        codigo2 = request.form["codigo2"]
        codigo3 = request.form["codigo3"]
        codigo4 = request.form["codigo4"]
        codigo_inserido = codigo1 + codigo2 + codigo3 + codigo4
        verification_code = session.get('verification_code')

        if codigo_inserido == verification_code:
            return redirect("/")  # Redireciona para a página principal após a verificação
        else:
            return render_template("verificacao.html", erro="Código incorreto. Tente novamente.")


# Rota para login de usuários
@app.route('/logar', methods=['GET', 'POST'])
def logar():
    if request.method == 'GET':
        return render_template('login.html')  # Exibe o formulário de login
    else:
        # Coleta os dados do formulário de login
        senha = request.form['senha']
        email = request.form['email']
        usuario = Usuario()  # Cria uma instância da classe Usuario
        usuario.logar(email, senha)  # Tenta fazer o login
        if usuario.logado:
            # Se o login for bem-sucedido, armazena os dados do usuário na sessão
            session['usuario_logado'] = {
                "nome": usuario.nome, 
                "email": usuario.email, 
                "tel": usuario.tel, 
                "id_cliente": usuario.id_cliente, 
                "tipo": usuario.tipo,
                "senha": usuario.senha
            }
            tipo = session.get('usuario_logado')['tipo']
            
            if tipo != 'cliente':
                return redirect("/adm")  # Redireciona para a página inicial do adm
            else:
                return redirect("/")  # Redireciona para a página inicial

        else:
            session.clear()  # Limpa a sessão em caso de falha no login
            return redirect("/logar")  # Redireciona para a página de login



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
    nome = request.form['nome']
    preco = request.form['preco']
    img = request.form['img']
    descricao = request.form['descricao']
    categoria = request.form['categoria']

    # Captura o tamanho da marmita (campo exibido apenas quando marmita for selecionada)
    tamanho = request.form.get('tamanho')

    # Captura as guarnições existentes
    guarnicoes_existentes = request.form.getlist('guarnicoes')

    # Captura as novas guarnições
    novas_guarnicoes = request.form.getlist('nova_guarnicoes')

    # Cria uma instância do objeto que contém o método de inserção
    adm = Adm()  # Substitua pelo seu objeto real

    # Verifica se a categoria selecionada é "Marmita"
    id_categoria_marmita = 7  # Substitua pelo ID real da categoria "Marmita"
    
    # Corrige a comparação para garantir que os tipos sejam compatíveis
    if int(categoria) == id_categoria_marmita:
        # Insere uma marmita
        sucesso = adm.inserir_marmita(nome, preco, img, descricao, tamanho, novas_guarnicoes)
    else:
        # Insere um produto normal
        sucesso = adm.inserir_produto(nome, preco, img, descricao, categoria, novas_guarnicoes)

    return redirect('/')  # Redireciona para a página inicial ou outra página desejada





@app.route("/exibir_guarnicao")
def exibir_guarnicao():
    adm = Adm()  # Cria uma instância da classe Sistema
    lista_guarnicao = adm.exibir_guarnição()  # Obtém a lista de guarnições
    categorias = adm.exibir_categorias()  # Obtém a lista de categorias de produtos
    return render_template("cad-produto.html", lista_guarnicao=lista_guarnicao, categorias=categorias)


@app.route('/adicionar_guarnicao', methods=['POST'])
def adicionar_guarnicao():
    nome_guarnicao = request.form.get('nome_guarnicao')
    adm = Adm()
    if nome_guarnicao:
        sucesso, id_guarnicao = adm.inserir_guarnicao(nome_guarnicao)  # Modifique a função para retornar o ID
        return jsonify(success=sucesso, id_guarnicao=id_guarnicao)
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
    lista_marunica = sistema.exibir_marmita(id_marmita)
    
    if lista_marunica is None:
        flash('Produto não encontrado.', 'error')
        return redirect('/')  # Ou outra página que faça sentido

    # Renderiza o template com os detalhes do produto
    return render_template("marmita.html", lista_marunica=lista_marunica)


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
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    else:
        adm = Adm()  # Cria uma instância da classe Adm
        lista_pedidos = adm.exibir_pedidos()  # Obtém a lista de pedidos
        return render_template('recebePedido.html', lista_pedidos=lista_pedidos)  # Passa a variável para o template



@app.route("/obter_pedidos", methods=['GET'])
def obter_pedidos():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona se não estiver logado
    else:
        adm = Adm()  # Cria uma instância da classe Sistema
        lista_pedidos = adm.exibir_pedidos()  # Obtém a lista de pedidos
        print(lista_pedidos)  # Debug: Verifique os dados retornados
        return jsonify(lista_pedidos)  # Retorna a lista de pedidos em formato JSON












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


# Rota para cancelar um pedido
@app.route("/cancelar_pedido", methods=['POST'])
def cancelar_pedido():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona se não estiver logado

    id_pedido = request.form.get('id_pedido')

    # Verifica se o ID do pedido é válido
    if id_pedido:
        sistema = Sistema()  # Cria uma instância da classe Sistema
        sucesso = sistema.cancelar_pedido(id_pedido)  # Função para cancelar o pedido no sistema
        
        if sucesso:
            return jsonify({'status': 'sucesso'})
        else:
            return jsonify({'status': 'erro', 'mensagem': 'Não foi possível cancelar o pedido.'})
    return jsonify({'status': 'erro', 'mensagem': 'Dados inválidos.'})


# Rota para enviar o carrinho como um pedido
@app.route("/enviar_carrinho", methods=['POST'])
def enviar_carrinho():
    if 'usuario_logado' in session:
        id_cliente = session['usuario_logado']['id_cliente']
        carrinho = Carrinho()
        if carrinho.enviar_carrinho(id_cliente):
            return jsonify(success=True, message="Pedido enviado com sucesso!", redirect="/exibir_pedidos")
        else:
            return jsonify(success=False, message="Erro ao enviar o carrinho.")
    return jsonify(success=False, message="Usuário não autenticado.")






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

    

# Rota para exibir o carrinho de compras
@app.route("/exibir_carrinho", methods=['GET', 'POST'])
def exibir_carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    else:
        carrinho = Carrinho()  # Cria uma instância da classe Sistema
        id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão

        if request.method == 'POST':
            if 'btn-excluir' in request.form:
                id_carrinho = request.form['btn-excluir']  # Obtém o ID do carrinho do produto a ser excluído
                carrinho.remover_produto_carrinho(id_carrinho)  # Remove o produto do carrinho
            else:
                # Atualiza a quantidade dos produtos no carrinho
                quantidades = request.form.getlist('quantidades')
                for id_carrinho, quantidade in quantidades.items():
                    carrinho.atualizar_quantidade_produto_carrinho(id_carrinho, quantidade)

        lista_carrinho = carrinho.exibir_carrinho(id_cliente)  # Obtém a lista de produtos no carrinho
        return render_template("carrinho.html", lista_carrinho=lista_carrinho)  # Renderiza a página do carrinho com a lista de produtos


    

@app.route("/inserir_carrinho", methods=['POST'])
def carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    else:
        if request.method == 'POST':
            id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão
            cod_produto = request.form.get('cod_produto')  # Obtém o ID do produto (pode ser None)
            id_marmita = request.form.get('id_marmita')  # Obtém o ID da marmita (pode ser None)

            carrinho = Carrinho()  # Cria uma instância da classe Carrinho
            if cod_produto or id_marmita:  # Garante que pelo menos um item foi enviado
                carrinho.inserir_item_carrinho(cod_produto, id_marmita, id_cliente)  # Adiciona o item ao carrinho do cliente
            else:
                print("Nenhum item foi selecionado para adicionar ao carrinho.")
            return redirect("/exibir_carrinho")  # Redireciona para a página do carrinho

        return redirect("/exibir_carrinho")  # Redireciona para a página do carrinho se o método não for POST




# Rota para inserir marmitas no carrinho
@app.route("/inserir_carrinho_marmita", methods=['POST'])
def carrinho_marmita():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    
    if request.method == 'POST':
        id_marmita = session.get('id', {}).get('id_marmita')  # Obtém o ID da marmita da sessão, com fallback
        id_cliente = session['usuario_logado']['id_cliente']  # Obtém o ID do cliente da sessão

        if 'IDs' not in session:
            session['IDs'] = {"IDs_produtos": []}  # Inicializa a lista de IDs de produtos na sessão

        session['IDs']['IDs_produtos'].append(id_marmita)  # Adiciona o ID da marmita à lista na sessão

        carrinho = Carrinho()  # Cria uma instância da classe Carrinho
        carrinho.inserir_item_carrinho(id_marmita, id_cliente, 'marmita')  # Adiciona a marmita ao carrinho do cliente
        return redirect("/exibir_carrinho")  # Redireciona para a página do carrinho

    return redirect("/exibir_carrinho")  # Redireciona para a página do carrinho se o método não for POST




@app.route("/editar_produto", methods=['POST', 'GET'])
def editar_produto():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    
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

    adm = Adm()  # Cria uma instância da classe Sistema
    id_produto = request.form.get('id_produto')
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    descricao = request.form.get('descricao')
    imagem = request.files.get('imagem')  # Para o upload de imagem

    # lógica para atualizar o produto no banco de dados
    adm.atualizar_produto(id_produto, nome, preco, descricao, imagem)

    flash('Produto atualizado com sucesso!', 'success')
    return redirect('/inicialadm')  # Ou para uma página de detalhes do produto


@app.route('/imagem_produto/<int:cod_produto>')
def imagem_produto(cod_produto):
    adm = Adm()  # Cria uma instância da classe Sistema
    imagem = adm.obter_imagem_produto(cod_produto)

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

    # Atualiza nome e imagem (sem alterar a senha)
    resultado = perfil.atualizar_perfil(id_cliente, nome, caminho_imagem)

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


app.run(debug=True)  # Executa o aplicativo Flask em modo de depuração


