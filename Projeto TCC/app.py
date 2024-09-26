from flask import Flask, render_template, request, redirect, session, jsonify
from usuario import Usuario
from sistema import Sistema

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Chave secreta para gerenciamento de sessões




# Rota para a página inicial
@app.route("/")
def principal():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos()  # Obtém a lista de produtos
    return render_template("index.html", lista_produtos=lista_produtos)  # Renderiza a página inicial com a lista de produtos


@app.route("/adm")
def principal_adm():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos()  # Obtém a lista de produtos
    return render_template("index-adm.html", lista_produtos=lista_produtos)  # Renderiza a página inicial com a lista de produtos


# Rota para cadastro de novos usuários
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == 'GET':
        usuario = Usuario()  # Cria uma instância da classe Usuario
        cursos = usuario.exibir_cursos()  # Obtém a lista de cursos disponíveis
        return render_template("cadastrar.html", cursos=cursos)  # Exibe o formulário de cadastro
    else:
        # Coleta os dados do formulário de cadastro
        nome = request.form["nome"]
        telefone = request.form["tel"]
        email = request.form["email"]
        senha = request.form["senha"]
        curso = request.form["curso"]
        tipo = "cliente"  # Tipo de usuário definido como cliente

        usuario = Usuario()  # Cria uma instância da classe Usuario
        if usuario.cadastrar(nome, telefone, email, senha, curso, tipo):
            return redirect("/")  # Redireciona para a página inicial se o cadastro for bem-sucedido
        else:
            return redirect("/cadastro")  # Redireciona para a página de cadastro em caso de erro




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





# Rota para inserção de novos produtos
@app.route("/inserir_produtos", methods=['GET', 'POST'])
def inserir_produtos():
    if request.method == 'GET':
        usuario = Usuario()  # Cria uma instância da classe Usuario
        categorias = usuario.exibir_categorias()  # Obtém a lista de categorias de produtos
        return render_template("cad-produto.html", categorias=categorias)  # Exibe o formulário de cadastro de produtos
    else:
        # Coleta os dados do formulário de inserção de produtos
        imagem_url = request.form["img"]
        nome_produto = request.form["nome"]
        preco_produto = request.form["preco"]
        categoria = request.form["categoria"]
        descricao = request.form["descricao"]

        usuario = Usuario()  # Cria uma instância da classe Usuario
        if usuario.inserir_produto(nome_produto, preco_produto, imagem_url, descricao, categoria):
            return redirect("/inserir_produtos")  # Redireciona para a página de inserção de produtos após sucesso
        else:
            return "ERRO AO INSERIR PRODUTO"  # Mensagem de erro em caso de falha




# Rota para exibição de produtos
@app.route("/exibir_produtos")
def compras():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    lista_produtos = sistema.exibir_produtos()  # Obtém a lista de produtos
    return render_template("produto.html", lista_produtos=lista_produtos)  # Renderiza a página com a lista de produtos




# Rota para exibir detalhes de um produto único
@app.route("/produto_unico", methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        sistema = Sistema()  # Cria uma instância da classe Sistema
        btn_produto = request.form.get('btn-produto')  # Obtém o ID do produto selecionado
        session['id'] = {"id_produto": btn_produto}  # Armazena o ID do produto na sessão
        lista_prounico = sistema.exibir_produto(btn_produto)  # Obtém os detalhes do produto
        return render_template("produto.html", lista_prounico=lista_prounico)  # Exibe os detalhes do produto




@app.route("/excluir_produto_adm", methods=['GET', 'POST'])
def excluir_produto_adm():
    sistema = Sistema()  # Cria uma instância da classe Sistema
    btn_excluir = request.form.get("btn-excluir")  # Obtém o ID do produto a ser excluído
    sistema.excluir_produto_adm(btn_excluir)  # Remove o produto
    return redirect("/adm")  # Redireciona para a página do carrinho



# Rota para exibir o perfil do usuário
@app.route("/perfil", methods=['GET', 'POST'])
def perfil():
    return render_template("perfil.html")  # Renderiza a página do perfil do usuário




# ========== Pedidos ==========
# Rota para exibir pedidos (para administradores)
@app.route("/exibir_pedidos", methods=['GET'])
def exibir_pedidos():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login
    else:
        sistema = Sistema()  # Cria uma instância da classe Sistema
        lista_pedidos = sistema.exibir_pedidos()  # Obtém a lista de pedidos
        return render_template('recebePedido.html', lista_pedidos=lista_pedidos)  # Passa a variável para o template




# Rota para obter os pedidos em JSON
@app.route("/obter_pedidos", methods=['GET'])
def obter_pedidos():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'redirect': '/logar'})  # Redireciona se não estiver logado
    else:
        sistema = Sistema()  # Cria uma instância da classe Sistema
        lista_pedidos = sistema.exibir_pedidos()  # Obtém a lista de pedidos
        return jsonify(lista_pedidos)  # Retorna a lista de pedidos em formato JSON





# Rota para enviar o carrinho como um pedido
@app.route("/enviar_carrinho", methods=['POST'])
def enviar_carrinho():
    if 'usuario_logado' in session:
        id_cliente = session['usuario_logado']['id_cliente']
        sistema = Sistema()
        sistema.enviar_carrinho(id_cliente)
        return jsonify(success=True, message="Pedido enviado com sucesso!", redirect="/exibir_pedidos")
    return jsonify(success=False, message="Erro ao enviar o carrinho.")








# ========== Carrinho ==========
    
# Rota para atualizar o preço total do carrinho via AJAX
@app.route("/atualizar_preco_total", methods=['GET'])
def atualizar_preco_total():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    id_cliente = session.get('usuario_logado')['id_cliente']

    try:
        sistema = Sistema()
        lista_carrinho = sistema.exibir_carrinho(id_cliente)
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

        sistema = Sistema()
        sistema.atualizar_quantidade_produto_carrinho(id_carrinho, quantidade)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Erro ao atualizar quantidade: {e}")
        return jsonify({'success': False, 'message': 'Erro ao atualizar quantidade'})
        



# Rota para excluir um produto
@app.route("/excluir_produto_carrinho", methods=['POST'])
def excluir_produto_carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        data = request.get_json()  # Obtém os dados JSON da requisição
        id_carrinho = data.get('id_carrinho')  # Obtém o ID do carrinho

        if not id_carrinho:
            return jsonify({'success': False, 'message': 'ID do carrinho não encontrado'})

        sistema = Sistema()  # Cria uma instância da classe Sistema
        sistema.remover_produto_carrinho(id_carrinho)  # Remove o produto do carrinho

        return jsonify({'success': True})  # Retorna sucesso se a exclusão for bem-sucedida

    except Exception as e:
        print(f"Erro ao excluir produto: {e}")  # Registra o erro no console
        return jsonify({'success': False, 'message': 'Erro ao excluir produto'})
    



# Rota para exibir o carrinho de compras
@app.route("/exibir_carrinho", methods=['GET', 'POST'])
def exibir_carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    else:
        sistema = Sistema()  # Cria uma instância da classe Sistema
        id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão

        if request.method == 'POST':
            if 'btn-excluir' in request.form:
                id_carrinho = request.form['btn-excluir']  # Obtém o ID do carrinho do produto a ser excluído
                sistema.remover_produto_carrinho(id_carrinho)  # Remove o produto do carrinho
            else:
                # Atualiza a quantidade dos produtos no carrinho
                quantidades = request.form.getlist('quantidades')
                for id_carrinho, quantidade in quantidades.items():
                    sistema.atualizar_quantidade_produto_carrinho(id_carrinho, quantidade)

        lista_carrinho = sistema.exibir_carrinho(id_cliente)  # Obtém a lista de produtos no carrinho
        return render_template("carrinho.html", lista_carrinho=lista_carrinho)  # Renderiza a página do carrinho com a lista de produtos
    



# Rota para inserir produtos no carrinho
@app.route("/inserir_carrinho", methods=['POST'])
def carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
    else:
        if request.method == 'POST':
            id_produto = session.get('id')['id_produto']  # Obtém o ID do produto da sessão
            id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão

            if 'IDs' not in session:
                session['IDs'] = {"IDs_produtos": []}  # Inicializa a lista de IDs de produtos na sessão

            session['IDs']['IDs_produtos'].append(id_produto)  # Adiciona o ID do produto à lista na sessão

            sistema = Sistema()  # Cria uma instância da classe Sistema
            sistema.inserir_produto_carrinho(id_produto, id_cliente)  # Adiciona o produto ao carrinho do cliente
            return redirect("/exibir_carrinho")  # Redireciona para a página do carrinho

        return redirect("/exibir_carrinho")  # Redireciona para a página do carrinho se o método não for POST



# # Rota para alterar a senha
# @app.route("trocar_senha", methods=['POST'])
# def trocar_senha():
#     if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
#         return redirect('/logar')  # Redireciona para a página de login se o usuário não estiver autenticado
#     else:
#         if request.method == 'POST':
#             sistema = Sistema()

#             id_cliente = session.get('usuario_logado')['id_cliente']  # Obtém o ID do cliente da sessão
#             senha_cliente = session.get('usuario_logado')['senha']  # Obtém a senha do cliente da sessão
#             sistema.trocar_senha(id_cliente, senha_cliente)


app.run(debug=True)  # Executa o aplicativo Flask em modo de depuração


