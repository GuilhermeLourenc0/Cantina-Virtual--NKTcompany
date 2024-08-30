from conexao import Conexao
from hashlib import sha256

class Usuario:
    def __init__(self):
        self.tel = None
        self.nome = None
        self.senha = None
        self.endereco = None
        self.cpf = None
        self.email = None
        self.imagem = None
        self.preco = None
        self.nomeP = None
        self.categoria = None
        self.descricao = None
        self.logado = False

    def cadastrar(self, nome, telefone, cpf, endereco, email, senha):
        senha = sha256(senha.encode()).hexdigest()
        try:
            mydb = Conexao.conectar()


            mycursor = mydb.cursor()

            
            sql = f"INSERT INTO tb_cliente VALUES('{nome}', {telefone}, '{cpf}', '{endereco}', '{email}', '{senha}')"
            
            mycursor.execute(sql)
            
            self.tel = telefone
            self.nome = nome
            self.senha = senha
            self.endereco = endereco
            self.cpf = cpf
            self.email = email
            self.logado = True


            mydb.commit()
            mydb.close()
            return True
        except:
            return False
        
    def logar(self, email, senha):
                # criptografa a senha
                senha = sha256(senha.encode()).hexdigest()

                mydb = Conexao.conectar()

                mycursor = mydb.cursor()

                sql = f"SELECT telefone, nome_cliente, senha, cpf FROM tb_cliente WHERE email='{email}' AND senha='{senha}'"
                
                mycursor.execute(sql)
            
                resultado = mycursor.fetchone()
                print(resultado)
                if not resultado == None:
                    self.logado = True
                    self.cpf = resultado[3]
                    self.nome = resultado[1]
                    self.tel = resultado[0]
                    self.senha = resultado[2]
                else:
                    self.logado = False
    def inserir_produto(self, imagem, nomeP, preco, categoria, descricao):
        # try:
            mydb = Conexao.conectar()
            mycursor = mydb.cursor()

            sql = f"INSERT INTO tb_produtos (imagem_produto, nome_produto, preco, categoria, descricao) VALUES('{imagem}', '{nomeP}', {preco}, '{categoria}', '{descricao}')"

            mycursor.execute(sql)

            self.imagem = imagem
            self.preco = preco
            self.nomeP = nomeP
            self.categoria = categoria
            self.descricao = descricao
            self.logado = True

            mydb.commit()
            mydb.close()
            return True
        # except:
        #     return False