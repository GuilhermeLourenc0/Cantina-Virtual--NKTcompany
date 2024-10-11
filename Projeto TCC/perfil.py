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

        
    def atualizar_perfil(self, id_cliente, nome, caminho_imagem=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            # Atualiza apenas o nome e a imagem, sem mudar a senha
            sql = "UPDATE tb_cliente SET nome_comp = %s"
            valores = [nome]

            # Verifica se o cliente já possui uma imagem
            mycursor.execute("SELECT imagem_binaria FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            imagem_existente = mycursor.fetchone()

            # Se uma nova imagem foi enviada
            if caminho_imagem:
                with open(caminho_imagem, 'rb') as imagem:
                    dados_imagem = imagem.read()

                # Atualiza a imagem binária, se existir ou adiciona a nova
                if imagem_existente and imagem_existente[0] is not None:
                    sql += ", imagem_binaria = %s"
                    valores.append(dados_imagem)
                else:
                    sql += ", imagem_binaria = %s"
                    valores.append(dados_imagem)

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
            mycursor.close()  # Fecha o cursor
            mydb.close()  # Fecha a conexão com o banco de dados


    def obter_perfil(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()
        
        try:
            print(f"Buscando perfil para id_cliente: {id_cliente}")  # Log do ID do cliente
            sql = "SELECT nome_comp, imagem_binaria FROM tb_cliente WHERE id_cliente = %s"
            mycursor.execute(sql, (id_cliente,))
            perfil = mycursor.fetchone()
            
            if perfil:
                nome, imagem = perfil
                if imagem is None:
                    imagem = '/static/img/default-avatar.png'  # Caminho para uma imagem padrão
                return {'nome': nome, 'imagem': imagem}  # Retorna um dicionário com nome e imagem
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