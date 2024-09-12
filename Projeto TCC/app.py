from flask import Flask, render_template, request, redirect, session
from usuario import Usuario
from sistema import Sistema




app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route("/")
def principal():

    sistema = Sistema()
    lista_produtos = sistema.exibir_produtos()
    return   render_template("index.html", lista_produtos = lista_produtos)

    

# Define cadastro route 
@app.route("/cadastro", methods = ["GET", "POST"])
def cadastro():
    if request.method == 'GET':
        usuario = Usuario()
        cursos = usuario.exibir_cursos()
        return render_template("cadastrar.html", cursos = cursos)
    else:
        nome = request.form["nome"]
        telefone = request.form["tel"]
        email = request.form["email"]
        senha = request.form["senha"]
        curso = request.form["curso"]
        tipo = "cliente"

        usuario = Usuario()
        if usuario.cadastrar(nome, telefone, email, senha, curso, tipo):
            return redirect("/")
        else:
            return redirect("/cadastro")
     
           
@app.route('/logar', methods = ['GET','POST'])
def logar():
    if request.method =='GET':
        return render_template('login.html')
    else:
        senha = request.form['senha']
        email = request.form['email']
        usuario = Usuario()
        usuario.logar(email, senha)
        if  usuario.logado == True:
            session['usuario_logado'] = {"nome": usuario.nome,
                                    "email": usuario.email,
                                    "tel": usuario.tel,
                                    "id_cliente": usuario.id_cliente}
            return redirect("/")
            
        else:
            session.clear()
            return redirect("/logar")
    
@app.route("/inserir_produtos", methods=['GET','POST'])
def inserir_produtos():
    if request.method == 'GET':
        usuario = Usuario()
        categorias = usuario.exibir_categorias()
        return render_template("cad-produto.html", categorias = categorias)
    else:
        imagem_url = request.form["img"]
        nome_produto = request.form["nome"]
        preco_produto = request.form["preco"]
        categoria = request.form["categoria"]
        descricao = request.form["descricao"]

        usuario = Usuario()

        if usuario.inserir_produto(nome_produto, preco_produto, imagem_url, descricao, categoria):
            return redirect("/inserir_produtos")
        else: 
            return "ERRO AO INSERIR PRODUTO"
        
@app.route("/exibir_produtos")
def compras():
   sistema = Sistema()
   lista_produtos = sistema.exibir_produtos()
   return   render_template("produto.html", lista_produtos = lista_produtos)


@app.route("/produto_unico", methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        sistema=Sistema()
        btn_produto = request.form.get('btn-produto')

        session['id'] = {"id_produto": btn_produto}
        lista_prounico = sistema.exibir_produto(btn_produto)
        return render_template("produto.html", lista_prounico = lista_prounico)
    

@app.route("/inserir_carrinho", methods=['POST'])
def carrinho():
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')
    else:
        if request.method == 'POST':
            id_produto = session.get('id')['id_produto']
            id_cliente = session.get('usuario_logado')['id_cliente']


            if 'IDs' not in session:
                session['IDs'] = {"IDs_produtos": []}  # Inicializa com uma lista vazia

            # Adiciona o novo ID do produto à lista na sessão
            session['IDs']['IDs_produtos'].append(id_produto)


            sistema = Sistema()
            sistema.inserir_produto_carrinho(id_produto, id_cliente)
            
            # Após inserir o comentário, redirecione para a rota que exibe os comentários
            return redirect("/exibir_carrinho")

        # Se por algum motivo o método for GET (não deveria ocorrer), redirecione também
        return redirect("/exibir_carrinho")
    
@app.route("/exibir_carrinho", methods=['GET', 'POST'])
def exibir_carrinho():
     if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('id_cliente') is None:
        return redirect('/logar')
     else:
        sistema = Sistema()
        id_clientes = session.get('usuario_logado')['id_cliente']
        lista_carrinho = sistema.exibir_carrinho(id_clientes)
        return render_template("carrinho.html", lista_carrinho = lista_carrinho)

@app.route("/excluir_produto", methods= ['GET', 'POST'])
def excluir_produto():
    sistema = Sistema()
    btn_excluir = request.form["btn-excluir"]

    sistema.excluir_produto(btn_excluir)
    return redirect("/exibir_carrinho")

@app.route("/enviar_carrinho", methods=['POST'])
def enviar_carrinho():
    if request.method == 'POST':
        id_carrinho = request.form["id_carrinho"]
        id_cliente = session.get('usuario_logado')['id_cliente']

    if id_carrinho and id_cliente:
        sistema = Sistema()
        sistema.enviar_carrinho(id_carrinho, id_cliente)
        
        # Redireciona para a rota que exibe os pedidos
        return redirect("/exibir_pedidos")

# @app.route("/nova_senha", methods=["POST"])
# def nova_senha():


app.run(debug=True)
