from conexao import Conexao
from hashlib import sha256

class Sistema:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


    def exibir_produtos_adm(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar todos os produtos
        sql = "SELECT * FROM tb_produto"
        mycursor.execute(sql)      # Executa a consulta
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        lista_produtos = []

        # Itera sobre os resultados e adiciona cada produto à lista
        for produto in resultado:
            lista_produtos.append({
                'nome_produto': produto[1],
                'preco': produto[2],
                'imagem_produto': produto[3],
                'categoria': produto[5],
                'descricao': produto[4],
                'id_produto': produto[0],
                'habilitado': produto[6]  # Certifique-se de que este índice corresponde ao campo 'habilitado'
            })
        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_produtos if lista_produtos else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado

    def exibir_produtos(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar apenas produtos habilitados (assumindo coluna 'habilitado')
        sql = "SELECT * FROM tb_produto WHERE habilitado = 1"
        mycursor.execute(sql)      # Executa a consulta
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        lista_produtos = []

        # Itera sobre os resultados e adiciona cada produto à lista
        for produto in resultado:
            lista_produtos.append({
                'nome_produto': produto[1],
                'preco': produto[2],
                'imagem_produto': produto[3],
                'categoria': produto[5],
                'descricao': produto[4],
                'id_produto': produto[0]
            })
        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_produtos if lista_produtos else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado


    # Método para exibir um único produto com base no ID
    def exibir_produto(self, id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para selecionar um produto específico pelo ID
        sql = "SELECT * FROM tb_produto WHERE cod_produto = %s"
        mycursor.execute(sql, (id,))
        resultado = mycursor.fetchone()  # Obtém o resultado único

        # Cria um dicionário para o produto
        dicionario_produto = {
            'nome_produto': resultado[1],
            'preco': resultado[2],
            'imagem_produto': resultado[3],
            'descricao': resultado[4],
            'cod_produto': resultado[0]
        }

        mydb.commit()
        mydb.close()
        return [dicionario_produto]  # Retorna a lista com um único produto
    


        # Método para exibir um único produto com base no ID
    def exibir_marmita(self, id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para selecionar um produto específico pelo ID
        sql = "SELECT * FROM tb_marmita WHERE id_marmita = %s"
        mycursor.execute(sql, (id,))
        resultado = mycursor.fetchone()  # Obtém o resultado único

        # Cria um dicionário para o produto
        dicionario_produto = {
                'nome_marmita': resultado[1],
                'preco': resultado[2],
                'imagem_marmita': resultado[5],
                'tamanho': resultado[3],
                'descricao': resultado[4],
                'id_marmita': resultado[0]
        }

        mydb.commit()
        mydb.close()
        return [dicionario_produto]  # Retorna a lista com um único produto


    def exibir_marmitas(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar apenas produtos habilitados (assumindo coluna 'habilitado')
        sql = "SELECT * FROM tb_marmita WHERE habilitado = 1"
        mycursor.execute(sql)      # Executa a consulta
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        lista_marmitas = []

        # Itera sobre os resultados e adiciona cada produto à lista
        for produto in resultado:
            lista_marmitas.append({
                'nome_marmita': produto[1],
                'preco': produto[2],
                'imagem_marmita': produto[5],
                'tamanho': produto[3],
                'descricao': produto[4],
                'id_marmita': produto[0]
            })
        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_marmitas if lista_marmitas else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado


   


    # Método para exibir todos os pedidos de um cliente específico com detalhes dos produtos
    def exibir_historico(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter todos os pedidos do cliente específico com detalhes dos produtos
        sql = """
            SELECT p.id_pedido, cl.id_cliente, cl.nome_comp, cl.telefone, 
                pr.nome_produto, pr.preco, pp.quantidade, 
                p.data_pedido, p.status
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            WHERE cl.id_cliente = %s  -- Filtra pelos pedidos do cliente específico
            ORDER BY p.data_pedido DESC, pr.nome_produto
        """
        mycursor.execute(sql, (id_cliente,))
        resultados = mycursor.fetchall()

        pedidos = {}

        # Itera sobre os resultados e organiza as informações de pedidos
        for resultado in resultados:
            id_pedido = resultado[0]
            nome_cliente = resultado[2]
            telefone_cliente = resultado[3]
            nome_produto = resultado[4]
            preco_produto = resultado[5]
            quantidade_produto = resultado[6]
            data_pedido = resultado[7]
            status_pedido = resultado[8]

            # Adiciona o cliente se não estiver no dicionário
            if id_cliente not in pedidos:
                pedidos[id_cliente] = {
                    'nome_cliente': nome_cliente,
                    'telefone': telefone_cliente,
                    'pedidos': {}
                }

            # Adiciona o pedido se não estiver no dicionário
            if id_pedido not in pedidos[id_cliente]['pedidos']:
                pedidos[id_cliente]['pedidos'][id_pedido] = {
                    'data_pedido': data_pedido,
                    'status': status_pedido,
                    'produtos': [],
                    'total_preco': 0  # Inicializa o total do pedido
                }

            # Adiciona o produto ao pedido e calcula o total
            total_produto = preco_produto * quantidade_produto
            pedidos[id_cliente]['pedidos'][id_pedido]['produtos'].append({
                'nome_produto': nome_produto,
                'preco': preco_produto,
                'quantidade': quantidade_produto
            })
            pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += total_produto  # Atualiza o total do pedido

        mydb.close()
        return pedidos



    def atualizar_status_pedido(self, id_pedido, novo_status):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            # Atualiza o status do pedido
            sql = "UPDATE tb_pedidos SET status = %s WHERE id_pedido = %s"
            mycursor.execute(sql, (novo_status, id_pedido))

            mydb.commit()  # Confirma a alteração
            return {"message": "Status atualizado com sucesso!"}  # Retorna mensagem de sucesso
        except Exception as e:
            mydb.rollback()  # Reverte a transação em caso de erro
            return {"error": f"Erro ao atualizar o status: {str(e)}"}
        finally:
            mydb.close()  # Fecha a conexão com o banco de dados



    def cancelar_pedido(self, id_pedido):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            # Atualiza o status do pedido para 'Cancelado'
            sql = "UPDATE tb_pedidos SET status = 'Cancelado' WHERE id_pedido = %s"
            mycursor.execute(sql, (id_pedido,))

            mydb.commit()  # Confirma a alteração
            return {"message": "Pedido cancelado com sucesso!"}  # Retorna mensagem de sucesso
        except Exception as e:
            mydb.rollback()  # Reverte a transação em caso de erro
            return {"error": f"Erro ao cancelar o pedido: {str(e)}"}
        finally:
            mydb.close()  # Fecha a conexão com o banco de dados