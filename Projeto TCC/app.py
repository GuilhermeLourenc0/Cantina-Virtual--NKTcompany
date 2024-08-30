from flask import Flask, render_template, request, redirect, session
from usuario import Usuario
from sistema import Sistema





app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route("/")
def principal():
    return render_template("index.html")
    

# Define cadastro route 
@app.route("/cadastro", methods = ["GET", "POST"])
def cadastro():
    if request.method == 'GET':
        return render_template("cadastro.html")
    else:
        nome = request.form["nome"]
        cpf = request.form["cpf"]
        telefone = request.form["telefone"]
        endereco = request.form["endereco"]
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario()

        if usuario.cadastrar(nome, telefone, cpf, endereco, email,senha):
            return redirect("/")
        else:
            return redirect("/cadastro")
     
           
# @app.route('/logar', methods = ['GET','POST'])
# def logar():
#     if request.method =='GET':
#         return render_template('login.html')
#     else:
#         senha = request.form['senha']
#         email = request.form['email']
#         usuario = Usuario()
#         usuario.logar(email, senha)
#         if  usuario.logado == True:
#             session['usuario_logado'] = {"nome": usuario.nome,
#                                     "email": usuario.email,
#                                     "cpf": usuario.cpf}
#             return redirect("/")
            
#         else:
#             session.clear()
#             return redirect("/logar")
    
# @app.route("/inserir_produtos", methods=['GET','POST'])
# def inserir_produtos():
#     if request.method == 'GET':
#         return render_template("venda.html")
#     else:
#         imagem_url = request.form["img"]
#         nome_produto = request.form["nome"]
#         preco_produto = request.form["preco"]
#         categoria = request.form["categoria"]
#         descricao = request.form["descricao"]

#         usuario = Usuario()

#         if usuario.inserir_produto(imagem_url, nome_produto, preco_produto, categoria, descricao):
#             return redirect("/")
#         else: 
#             return "ERRO AO INSERIR PRODUTO"
        
# @app.route("/produtos")
# def compras():
#    sistema = Sistema()
#    lista_categoria = sistema.exibir_produtos()
#    return   render_template("produtos.html", lista_categoria = lista_categoria)

# @app.route("/categoria/<categoria>")
# def catgoria(categoria):

#     sistema = Sistema()
#     lista_filtro = sistema.filtro(categoria)
    
#     return render_template("produtos-categoria.html",  lista_filtro = lista_filtro)


# @app.route("/compra", methods=['GET', 'POST'])
# def comprar():
#     if request.method == 'POST':
#         sistema=Sistema()
#         btn_produto = request.form.get('btn-produto')

#         session['id'] = {"id_produto": btn_produto}
#         lista_carrinho = sistema.exibir_produto(btn_produto)
#         return render_template("produto-unico.html", lista_carro = lista_carrinho)
    

# @app.route("/inserir_carrinho", methods=['POST'])
# def carrinho():
#     if 'usuario_logado' not in session or session['usuario_logado'] is None or session['usuario_logado'].get('cpf') is None:
#         return redirect('/logar')
#     else:
#         if request.method == 'POST':
#             id_produto = session.get('id')['id_produto']
#             cpf_cliente = session.get('usuario_logado')['cpf']
#             sistema = Sistema()
#             sistema.inserir_produto_carrinho(id_produto, cpf_cliente)
            
#             # Após inserir o comentário, redirecione para a rota que exibe os comentários
#             return redirect("/exibir_carrinho")

#         # Se por algum motivo o método for GET (não deveria ocorrer), redirecione também
#         return redirect("/exibir_carrinho")
    
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
