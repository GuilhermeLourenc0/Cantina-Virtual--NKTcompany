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
        tipo = request.form["tipo"]

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
                                    "tel": usuario.tel}
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

# @app.route("/categoria/<categoria>")
# def catgoria(categoria):

#     sistema = Sistema()
#     lista_filtro = sistema.filtro(categoria)
    
#     return render_template("produtos-categoria.html",  lista_filtro = lista_filtro)


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
    if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('cpf') is None:
        return redirect('/logar')
    else:
        if request.method == 'POST':
            id_produto = session.get('id')['id_produto']
            tel_cliente = session.get('usuario_logado')['tel']
            sistema = Sistema()
            sistema.inserir_produto_carrinho(id_produto, tel_cliente)
            
            # Após inserir o comentário, redirecione para a rota que exibe os comentários
            return redirect("/exibir_carrinho")

        # Se por algum motivo o método for GET (não deveria ocorrer), redirecione também
        return redirect("/exibir_carrinho")
    
# @app.route("/exibir_carrinho", methods=['GET', 'POST'])
# def exibir_carrinho():
#      if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('cpf') is None:
#         return redirect('/logar')
#      else:
#         sistema = Sistema()
#         cpf = session.get('usuario_logado')['cpf']
#         lista_carrinho = sistema.exibir_carrinho(cpf)
#         return render_template("carrinho.html", lista_carro=lista_carrinho)

# @app.route("/inserir_comentario", methods=['GET', 'POST'])
# def comentario():
#     if request.method == 'POST':
#         comentario = request.form['comentario']
#         nome_cliente = session.get('usuario_logado')['nome']
#         sistema = Sistema()
#         sistema.inserir_comentario(comentario, nome_cliente)
        
#         # Após inserir o comentário, redirecione para a rota que exibe os comentários
#         return redirect("/exibir_comentario")
    
#     # Se por algum motivo o método for GET (não deveria ocorrer), redirecione também
#     return redirect("/exibir_comentario")

# @app.route("/exibir_comentario", methods=['GET'])
# def exibir_comentario():
#      if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('cpf') is None:
#         return redirect('/logar')
#      else:
#         sistema = Sistema()
#         nome_cliente = session.get('usuario_logado')['nome']
#         lista_comentario = sistema.exibir_comentario(nome_cliente)
#         return render_template("comentario.html", lista_comentario=lista_comentario)

# @app.route("/excluir_produto", methods= ['GET', 'POST'])
# def excluir_produto():
#     sistema = Sistema()
#     btn_excluir = request.form["btn-excluir"]

#     sistema.excluir_produto(btn_excluir)
#     return redirect("/exibir_carrinho")

app.run(debug=True)
