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

    # Função de cadastro do usuário
    def cadastrar(self, nome, telefone, email, senha, curso, tipo):
        senha = sha256(senha.encode()).hexdigest()  # Criptografa a senha usando o algoritmo sha256
        
        try:
            mydb = Conexao.conectar()  # Conecta ao banco de dados
            mycursor = mydb.cursor()

            # Verifica se o email ou telefone já estão cadastrados
            mycursor.execute(
                "SELECT id_cliente FROM tb_cliente WHERE email = %s OR telefone = %s",
                (email, telefone)
            )
            existing_user = mycursor.fetchone()
            
            if existing_user:
                # Retorna False para indicar que o cadastro foi impedido por duplicidade
                return False

            # Insere o novo usuário caso não haja duplicidade
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

    def verificar_duplicidade(self, email, telefone):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT id_cliente FROM tb_cliente WHERE email = %s OR telefone = %s",
            (email, telefone)
        )
        return bool(mycursor.fetchone())


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

        try:
            # Query SQL para verificar se o email e a senha correspondem a um registro no banco de dados
            sql = "SELECT * FROM tb_cliente WHERE email = %s AND senha = %s"
            mycursor.execute(sql, (email, senha))

            # Busca um único registro (se houver)
            resultado = mycursor.fetchone()

            # Se um registro for encontrado, atualiza os atributos do usuário
            if resultado:
                self.logado = True
                self.id_cliente = resultado[0]
                self.nome = resultado[1]
                self.tel = resultado[2]
                self.email = resultado[3]
                self.senha = resultado[5]
                self.tipo = resultado[6]
                self.primeiro_login = bool(resultado[8])  # Converte para bool
            else:
                self.logado = False
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            mycursor.close()
            mydb.close()



    def atualizar_dados(self, id_cliente, telefone, email, senha):
        """
        Atualiza o telefone, email e senha do administrador e define 'primeiro_login' como False.
        
        Parâmetros:
        - id_cliente: ID do cliente (administrador) a ser atualizado
        - telefone: Novo número de telefone
        - email: Novo email
        - senha: Nova senha em texto puro que será criptografada para o banco de dados
        
        Retorno:
        - True se a atualização for bem-sucedida, False caso contrário
        """
        # Hash da senha antes de armazenar no banco
        hashed_password = sha256(senha.encode()).hexdigest()
        
        # Conecta ao banco de dados
        mydb = Conexao.conectar()  
        mycursor = mydb.cursor()

        try:
            # Query para atualizar os dados do administrador e marcar `primeiro_login` como `False`
            sql = """
                UPDATE tb_cliente
                SET telefone = %s, email = %s, senha = %s, primeiro_login = %s
                WHERE id_cliente = %s
            """
            valores = (telefone, email, hashed_password, False, id_cliente)

            # Executa a query
            mycursor.execute(sql, valores)
            mydb.commit()
            
            # Atualiza o atributo `primeiro_login` localmente
            self.primeiro_login = False
            return True
        except Exception as e:
            print("Erro ao atualizar dados do administrador:", e)
            mydb.rollback()
            return False
        finally:
            # Fecha o cursor e a conexão
            mycursor.close()
            mydb.close()


    def atualizar_telefone(self, id_cliente, telefone):
        """
        Atualiza o telefone do cliente no banco de dados.

        Parâmetros:
        - id_cliente: ID do cliente que terá o telefone atualizado
        - telefone: Novo número de telefone a ser salvo

        Retorno:
        - True se a atualização for bem-sucedida, False caso contrário
        """
        # Conectar ao banco de dados
        mydb = Conexao.conectar()  
        mycursor = mydb.cursor()

        try:
            # Comando SQL para atualizar o telefone
            sql = "UPDATE tb_cliente SET telefone = %s WHERE id_cliente = %s"
            valores = (telefone, id_cliente)

            # Executa a atualização
            mycursor.execute(sql, valores)
            mydb.commit()
            print("Telefone atualizado com sucesso!")
            return True
        except Exception as e:
            print("Erro ao atualizar o telefone:", e)
            mydb.rollback()
            return False
        finally:
            # Fecha o cursor e a conexão com o banco
            mycursor.close()
            mydb.close()


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
    

    def tela_usuario(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Modifica a consulta SQL para incluir o INNER JOIN com tb_curso
        sql = f"""
            SELECT c.id_cliente, c.nome_comp, c.telefone, c.email, c.tipo, cu.curso 
            FROM tb_cliente c 
            INNER JOIN tb_curso cu ON c.id_curso = cu.id_curso 
            WHERE c.id_cliente = {id_cliente}
        """
        
        mycursor.execute(sql)

        resultado = mycursor.fetchone()  # Use fetchone para obter um único registro

        # Cria um dicionário com os dados do cliente e o nome do curso
        if resultado:
            cliente_dict = {
                "id_cliente": resultado[0],
                "nome_comp": resultado[1],
                "telefone": resultado[2],
                "email": resultado[3],
                "nome_curso": resultado[5]  # Adiciona o nome do curso ao dicionário
            }
        else:
            cliente_dict = None

        mydb.close()  # Fecha a conexão

        return cliente_dict  # Retorna o dicionário com os dados do cliente e o nome do curso


