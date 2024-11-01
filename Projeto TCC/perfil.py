from conexao import Conexao
from hashlib import sha256

class Perfil:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


    def verificar_senha(self, id_cliente, senha_fornecida):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            senha_fornecida = sha256(senha_fornecida.encode()).hexdigest()
            # Busca a senha atual do cliente no banco de dados
            mycursor.execute("SELECT senha FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            senha_armazenada = mycursor.fetchone()

            if senha_armazenada is None:
                print("Cliente não encontrado.")  # Log para depuração
                return False  # Se o cliente não for encontrado

            # Verifica se a senha fornecida é igual à senha armazenada
            return senha_armazenada[0] == senha_fornecida  # Retorna True ou False

        except Exception as e:
            print(f"Erro ao verificar a senha: {str(e)}")  # Log do erro
            return {"error": f"Erro ao verificar a senha: {str(e)}"}

        finally:
            mycursor.close()  # Fecha o cursor
            mydb.close()  # Fecha a conexão com o banco de dados

        
    def atualizar_perfil(self, id_cliente, nome=None, caminho_imagem=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            # Inicia a query de atualização
            sql = "UPDATE tb_cliente SET"
            valores = []

            # Atualiza o nome apenas se ele for fornecido (não vazio)
            if nome:
                sql += " nome_comp = %s"
                valores.append(nome)

            # Se uma nova imagem foi enviada
            if caminho_imagem:
                if nome:
                    sql += ","  # Adiciona uma vírgula se o nome já foi incluído
                sql += " imagem_binaria = %s"
                with open(caminho_imagem, 'rb') as imagem:
                    dados_imagem = imagem.read()
                valores.append(dados_imagem)

            # Se nenhuma alteração foi feita
            if not valores:
                return {"message": "Nenhuma alteração feita no perfil."}

            # Adiciona a condição para o WHERE
            sql += " WHERE id_cliente = %s"
            valores.append(id_cliente)

            # Executa a query de atualização
            print(f"Executando SQL: {sql}, com valores: {valores}")  # Log para depuração
            mycursor.execute(sql, valores)
            mydb.commit()

            return {"message": "Perfil atualizado com sucesso!"}
        
        except Exception as e:
            mydb.rollback()
            print(f"Erro ao atualizar o perfil: {str(e)}")  # Log do erro
            return {"error": f"Erro ao atualizar o perfil: {str(e)}"}
        
        finally:
            mycursor.close()
            mydb.close()




    def obter_perfil(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            print(f"Buscando perfil para id_cliente: {id_cliente}")  # Log do ID do cliente
            sql = """SELECT c.nome_comp, c.imagem_binaria, curso.curso 
                    FROM tb_cliente c 
                    INNER JOIN tb_curso curso ON c.id_curso = curso.id_curso 
                    WHERE c.id_cliente = %s;"""
            mycursor.execute(sql, (id_cliente,))
            perfil = mycursor.fetchone()

            if perfil:
                nome, imagem, curso = perfil
                return {'nome': nome, 'imagem': imagem, 'curso': curso}  # Retorna o nome, imagem e curso
            return None  # Retorna None se não houver perfil
        except Exception as e:
            print(f"Erro ao obter perfil: {e}")  # Log de erro
            return None  # Lida com qualquer erro
        finally:
            mycursor.close()
            mydb.close()






    def obter_imagem_perfil(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("SELECT imagem_binaria FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            imagem = mycursor.fetchone()
            return imagem[0] if imagem else None
        except Exception as e:
            return None
        finally:
            mycursor.close()
            mydb.close()