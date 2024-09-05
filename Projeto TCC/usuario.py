from conexao import Conexao
from hashlib import sha256

class Usuario:
    def __init__(self):
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
        senha = sha256(senha.encode()).hexdigest()  # Criptografando a senha
        try:
            mydb = Conexao.conectar()  # Conectando ao banco de dados
            mycursor = mydb.cursor()

            # Especificando as colunas da tabela tb_cliente e usando placeholders (%s)
            sql = "INSERT INTO tb_cliente (nome_comp, telefone, email, id_curso, senha, tipo) VALUES (%s, %s, %s, %s, %s, %s)"
            
            # Executando a query com os valores fornecidos
            mycursor.execute(sql, (nome, telefone, email, curso, senha, tipo))

            # Atribuindo valores aos atributos do objeto
            self.tel = telefone
            self.nome = nome
            self.senha = senha
            self.curso = curso
            self.email = email
            self.tipo = tipo
            self.logado = True

            mydb.commit()  # Confirmando as alterações no banco de dados


            mydb.close()  # Fechando a conexão
            return True
        except Exception as e:
            print(f"Ocorreu um erro: {e}")  # Exibindo a mensagem de erro
            return False

    def exibir_cursos(self):
            mydb = Conexao.conectar()  # Conectando ao banco de dados
            mycursor = mydb.cursor()

            sql = f"SELECT * from tb_curso"
            mycursor.execute(sql)
        
            resultado = mycursor.fetchall()
       
            lista_cursos = []

            for cursos in resultado:
                lista_cursos.append({
                    'id_curso': cursos[0],
                    'curso': cursos[1]
            })

            mydb.commit()  # Confirmando as alterações no banco de dados
            mydb.close()  # Fechando a conexão
            return lista_cursos
        
    def logar(self, email, senha):
                senha = sha256(senha.encode()).hexdigest()  # Criptografando a senha
                mydb = Conexao.conectar()

                mycursor = mydb.cursor()

                sql = f"SELECT * FROM tb_cliente WHERE email='{email}' AND senha='{senha}'"
                
                mycursor.execute(sql)
            
                resultado = mycursor.fetchone()
                print(resultado)
                if not resultado == None:
                    self.logado = True
                    self.nome = resultado[1]
                    self.tel = resultado[2]
                    self.senha = resultado[5]
                    self.email = resultado[3]
                else:
                    self.logado = False

    def inserir_produto(self, nomeP, preco, imagem, descricao):
        # try:
            mydb = Conexao.conectar()
            mycursor = mydb.cursor()

            sql = f"INSERT INTO tb_produto (nome_produto, preco, url_img, descricao) VALUES('{nomeP}', {preco}, '{imagem}', '{descricao}')"

            mycursor.execute(sql)

            self.imagem = imagem
            self.preco = preco
            self.nomeP = nomeP
            # self.categoria = categoria
            self.descricao = descricao
            self.logado = True

            mydb.commit()
            mydb.close()
            return True
        # except:
        #     return False