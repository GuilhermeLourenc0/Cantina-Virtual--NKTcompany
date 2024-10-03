from conexao import Conexao
from hashlib import sha256

class Usuario:
    
    """
    Classe responsável por gerenciar as operações de usuários e produtos no sistema.
    Essa classe oferece funcionalidades como cadastrar usuários, logar, exibir cursos e categorias, 
    inserir produtos, entre outras operações relacionadas ao usuário e suas interações com o sistema.
    """
    
    def __init__(self):
        """
        Método inicializador que define os atributos da classe Usuario. Esses atributos
        armazenam informações como telefone, nome, senha, email, curso, tipo, e o estado de login do usuário.
        """
        self.tel = None
        self.nome = None
        self.senha = None
        self.email = None
        self.imagem = None
        self.preco = None
        self.nomeP = None
        self.categoria = None
        self.descricao = None
        self.curso = None
        self.tipo = None
        self.logado = False

    def cadastrar(self, nome, telefone, email, senha, curso, tipo):
        """
        Cadastra um novo usuário no sistema, recebendo as informações de nome, telefone, email, senha (criptografada),
        curso e tipo de usuário. Insere esses dados na tabela `tb_cliente` e, se a operação for bem-sucedida, 
        atualiza os atributos da classe e marca o usuário como logado.
        
        Parâmetros:
        - nome: nome completo do usuário.
        - telefone: número de telefone do usuário.
        - email: endereço de email do usuário.
        - senha: senha do usuário, que será criptografada.
        - curso: ID do curso selecionado pelo usuário.
        - tipo: tipo de usuário (cliente, administrador, etc.).
        
        Retorno:
        - Retorna True se o cadastro for realizado com sucesso; caso contrário, retorna False.
        """
        senha = sha256(senha.encode()).hexdigest()  # Criptografa a senha usando o algoritmo sha256
        
        try:
            mydb = Conexao.conectar()  # Conecta ao banco de dados
            mycursor = mydb.cursor()
            
            # Query SQL para inserir os dados do novo usuário
            sql = "INSERT INTO tb_cliente (nome_comp, telefone, email, id_curso, senha, tipo) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(sql, (nome, telefone, email, curso, senha, tipo))
            
            # Atualiza os atributos do objeto
            self.tel = telefone
            self.nome = nome
            self.senha = senha
            self.curso = curso
            self.email = email
            self.tipo = tipo
            self.logado = True  # Marca o usuário como logado
            
            mydb.commit()  # Confirma as alterações no banco de dados
            mydb.close()  # Fecha a conexão
            return True
        except Exception as e:
            print(f"Ocorreu um erro: {e}")  # Exibe uma mensagem de erro em caso de falha
            return False

    def exibir_cursos(self):
        """
        Retorna uma lista com todos os cursos disponíveis no sistema, consultando a tabela `tb_curso`.
        Cada curso contém o ID do curso e o nome do curso.
        
        Retorno:
        - Uma lista de dicionários, onde cada dicionário representa um curso com 'id_curso' e 'curso'.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para selecionar todos os cursos
        sql = "SELECT * from tb_curso"
        mycursor.execute(sql)

        # Obtém os resultados e os organiza em uma lista
        resultado = mycursor.fetchall()
        lista_cursos = [{'id_curso': curso[0], 'curso': curso[1]} for curso in resultado]

        mydb.commit()
        mydb.close()
        return lista_cursos

    def exibir_categorias(self):
        """
        Retorna uma lista com todas as categorias de produtos disponíveis, consultando a tabela `tb_categoria`.
        Cada categoria contém o ID da categoria e o nome da categoria.
        
        Retorno:
        - Uma lista de dicionários, onde cada dicionário representa uma categoria com 'id_categoria' e 'nome'.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para selecionar todas as categorias
        sql = "SELECT * from tb_categoria"
        mycursor.execute(sql)

        # Obtém os resultados e os organiza em uma lista
        resultado = mycursor.fetchall()
        lista_categorias = [{'id_categoria': categoria[0], 'nome': categoria[1]} for categoria in resultado]

        mydb.commit()
        mydb.close()
        return lista_categorias

    def logar(self, email, senha):
        """
        Realiza o login de um usuário verificando o email e a senha criptografada no banco de dados.
        Se a combinação for encontrada, o estado do usuário é marcado como logado e os dados do usuário
        são carregados para os atributos da classe.
        
        Parâmetros:
        - email: endereço de email do usuário.
        - senha: senha do usuário, que será criptografada antes da verificação.
        
        Retorno:
        - None. O estado de login e os dados do usuário são atualizados nos atributos da classe.
        """
        senha = sha256(senha.encode()).hexdigest()  # Criptografa a senha usando o algoritmo sha256
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para verificar se o email e a senha correspondem a um registro no banco de dados
        sql = f"SELECT * FROM tb_cliente WHERE email='{email}' AND senha='{senha}'"
        mycursor.execute(sql)

        # Busca um único registro (se houver)
        resultado = mycursor.fetchone()
        
        # Se um registro for encontrado, atualiza os atributos do usuário
        if resultado:
            self.logado = True
            self.id_cliente = resultado[0]
            self.nome = resultado[1]
            self.tel = resultado[2]
            self.senha = resultado[5]
            self.tipo = resultado[6]
            self.email = resultado[3]
        else:
            self.logado = False

    def logout(self, id_cliente):
        """
        Realiza o logout do usuário removendo os itens do carrinho de compras associado ao cliente.
        Ao fazer logout, o carrinho é esvaziado.
        
        Parâmetros:
        - id_cliente: o ID do cliente que está realizando o logout.
        
        Retorno:
        - None.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para remover os itens do carrinho do cliente
        sql_remover_carrinho = f"DELETE FROM tb_carrinho WHERE id_cliente={id_cliente}"
        mycursor.execute(sql_remover_carrinho)
        mydb.commit()  # Confirma as alterações
        mydb.close()  # Fecha a conexão

    def inserir_produto(self, nomeP, preco, imagem, descricao, categoria):
        """
        Insere um novo produto no sistema, associando-o à categoria correta. As informações do produto
        incluem nome, preço, URL da imagem, descrição e a categoria do produto.
        
        Parâmetros:
        - nomeP: nome do produto.
        - preco: preço do produto.
        - imagem: URL da imagem do produto.
        - descricao: breve descrição do produto.
        - categoria: ID da categoria à qual o produto pertence.
        
        Retorno:
        - Retorna True se o produto for inserido com sucesso, ou False em caso de erro.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para inserir o produto na tabela `tb_produto`
        sql = f"INSERT INTO tb_produto (nome_produto, preco, url_img, descricao, id_categoria) VALUES ('{nomeP}', {preco}, '{imagem}', '{descricao}', {categoria})"
        mycursor.execute(sql)

        # Atualiza os atributos do objeto com os dados do produto
        self.imagem = imagem
        self.preco = preco
        self.nomeP = nomeP
        self.categoria = categoria
        self.descricao = descricao
        self.logado = True  # Marca o usuário como logado após a inserção do produto

        mydb.commit()  # Confirma as alterações no banco de dados
        mydb.close()  # Fecha a conexão
        return True



    def verificar_usuario(self, email, telefone):
        """
        Verifica se um usuário com o email e telefone fornecidos existe no sistema.

        Parâmetros:
        - email: endereço de email do usuário.
        - telefone: número de telefone do usuário.

        Retorno:
        - Retorna True se o usuário existir; caso contrário, retorna False.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para verificar se o email e telefone existem na tabela tb_cliente
        sql = "SELECT * FROM tb_cliente WHERE email = %s AND telefone = %s"
        mycursor.execute(sql, (email, telefone))
        
        resultado = mycursor.fetchone()  # Busca um único registro
        
        mydb.close()  # Fecha a conexão

        return resultado is not None  # Retorna True se o usuário existir, False caso contrário

    def atualizar_senha(self, email, nova_senha):
        """
        Atualiza a senha de um usuário no sistema. A nova senha é criptografada antes de ser armazenada.
        
        Parâmetros:
        - email: endereço de email do usuário.
        - nova_senha: nova senha que será criptografada e atualizada no banco de dados.
        
        Retorno:
        - Retorna True se a atualização da senha for realizada com sucesso; caso contrário, retorna False.
        """
        nova_senha = sha256(nova_senha.encode()).hexdigest()  # Criptografa a nova senha usando o algoritmo sha256

        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para atualizar a senha na tabela tb_cliente
        sql = "UPDATE tb_cliente SET senha = %s WHERE email = %s"
        mycursor.execute(sql, (nova_senha, email))

        mydb.commit()  # Confirma as alterações
        mydb.close()  # Fecha a conexão
        
        return mycursor.rowcount > 0  # Retorna True se a senha foi atualizada, False caso contrário