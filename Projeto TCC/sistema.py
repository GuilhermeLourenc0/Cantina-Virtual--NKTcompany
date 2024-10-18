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
    


    def exibir_marmita(self, id_marmita):
        # Conexão e consulta ao banco
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para selecionar a marmita, guarnições e acompanhamentos associados
        sql_marmita = """
        SELECT 
            m.id_marmita, m.nome_marmita, m.preco, m.tamanho, m.descricao, m.url_img,
            GROUP_CONCAT(DISTINCT CONCAT(g.id_guarnicao, ':', g.nome_guarnicao) SEPARATOR ', ') AS guarnicoes,
            GROUP_CONCAT(DISTINCT CONCAT(a.id_acompanhamento, ':', a.nome_acompanhamento) SEPARATOR ', ') AS acompanhamentos
        FROM 
            tb_marmita AS m
        LEFT JOIN tb_marmita_guarnicao AS mg ON m.id_marmita = mg.id_marmita
        LEFT JOIN tb_guarnicao AS g ON mg.id_guarnicao = g.id_guarnicao
        LEFT JOIN tb_marmita_acompanhamento AS ma ON m.id_marmita = ma.id_marmita
        LEFT JOIN tb_acompanhamentos AS a ON ma.id_acompanhamento = a.id_acompanhamento
        WHERE m.id_marmita = %s
        GROUP BY m.id_marmita;
        """
        mycursor.execute(sql_marmita, (id_marmita,))
        resultado = mycursor.fetchone()

        # Caso a consulta não encontre resultados
        if not resultado:
            return None

        # Função auxiliar para dividir os resultados de guarnições e acompanhamentos
        def processar_itens(itens):
            if not itens:
                return []
            lista_itens = []
            for item in itens.split(', '):
                id_item, nome_item = item.split(':')
                lista_itens.append({'id': id_item, 'nome': nome_item})
            return lista_itens

        # Processa guarnições e acompanhamentos associados à marmita
        guarnicoes_associadas = processar_itens(resultado[6])  # IDs e nomes das guarnições
        acompanhamentos_associados = processar_itens(resultado[7])  # IDs e nomes dos acompanhamentos

        # Consulta SQL para pegar todas as guarnições
        sql_todas_guarnicoes = "SELECT id_guarnicao, nome_guarnicao FROM tb_guarnicao"
        mycursor.execute(sql_todas_guarnicoes)
        todas_guarnicoes = [{'id': str(row[0]), 'nome': row[1]} for row in mycursor.fetchall()]

        # Consulta SQL para pegar todos os acompanhamentos
        sql_todos_acompanhamentos = "SELECT id_acompanhamento, nome_acompanhamento FROM tb_acompanhamentos"
        mycursor.execute(sql_todos_acompanhamentos)
        todos_acompanhamentos = [{'id': str(row[0]), 'nome': row[1]} for row in mycursor.fetchall()]

        # Organiza os dados da marmita
        dados_marmita = {
            'id_marmita': resultado[0],  # ID da marmita
            'nome_marmita': resultado[1],  # Nome da marmita
            'preco': resultado[2],  # Preço
            'tamanho': resultado[3],  # Tamanho
            'descricao': resultado[4],  # Descrição
            'imagem_marmita': resultado[5],  # Imagem
            'guarnicoes': guarnicoes_associadas,  # Guarnições associadas à marmita
            'acompanhamentos': acompanhamentos_associados,  # Acompanhamentos associados à marmita
            'todas_guarnicoes': todas_guarnicoes,  # Todas as guarnições disponíveis
            'todos_acompanhamentos': todos_acompanhamentos  # Todos os acompanhamentos disponíveis
        }

        # Fecha a conexão
        mydb.close()

        # Retorna a lista com o dicionário da marmita
        return [dados_marmita]












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
    
    def exibir_marmitas_adm(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar todos os produtos
        sql = "SELECT * FROM tb_marmita"
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
                    'id_marmita': produto[0],
                    'habilitado': produto[6]  # Certifique-se de que este índice corresponde ao campo 'habilitado'
                })
        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_marmitas if lista_marmitas else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado


   


    # Método para exibir todos os pedidos de um cliente específico com detalhes dos produtos e marmitas
    def exibir_historico(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter todos os pedidos do cliente específico com detalhes dos produtos e marmitas
        sql = """
            SELECT p.id_pedido, cl.id_cliente, cl.nome_comp, cl.telefone, 
                pr.nome_produto, pr.preco AS preco_produto, pp.quantidade, 
                m.nome_marmita, m.preco AS preco_marmita, 
                p.data_pedido, p.status
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE cl.id_cliente = %s  -- Filtra pelos pedidos do cliente específico
            ORDER BY p.data_pedido DESC
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
            nome_marmita = resultado[7]
            preco_marmita = resultado[8]
            data_pedido = resultado[9]
            status_pedido = resultado[10]

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
                    'marmitas': [],
                    'guarnicoes': [],  # Inicializa a lista de guarnições
                    'acompanhamentos': [],  # Inicializa a lista de acompanhamentos
                    'total_preco': 0  # Inicializa o total do pedido
                }

            # Adiciona o produto ao pedido, se houver
            if nome_produto:
                total_produto = preco_produto * quantidade_produto
                pedidos[id_cliente]['pedidos'][id_pedido]['produtos'].append({
                    'nome_produto': nome_produto,
                    'preco': preco_produto,
                    'quantidade': quantidade_produto
                })
                pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += total_produto  # Atualiza o total do pedido

            # Adiciona a marmita ao pedido, se houver
            if nome_marmita:
                pedidos[id_cliente]['pedidos'][id_pedido]['marmitas'].append({
                    'nome_marmita': nome_marmita,
                    'preco': preco_marmita
                })
                pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += preco_marmita  # Atualiza o total do pedido

        # Buscar guarnições e acompanhamentos para cada pedido
        for id_pedido in pedidos[id_cliente]['pedidos']:
            # Buscar guarnições
            sql_guarnicoes = """
                SELECT g.nome_guarnicao 
                FROM tb_guarnicoes_pedidos AS cg
                JOIN tb_guarnicao AS g ON cg.id_guarnicao = g.id_guarnicao
                WHERE cg.id_pedido = %s
            """
            mycursor.execute(sql_guarnicoes, (id_pedido,))
            guarnicoes = [row[0] for row in mycursor.fetchall()]
            pedidos[id_cliente]['pedidos'][id_pedido]['guarnicoes'] = guarnicoes  # Adiciona as guarnições ao pedido

            # Buscar acompanhamentos
            sql_acompanhamentos = """
                SELECT a.nome_acompanhamento 
                FROM tb_acompanhamentos_pedidos AS ca
                JOIN tb_acompanhamentos AS a ON ca.id_acompanhamento = a.id_acompanhamento
                WHERE ca.id_pedido = %s
            """
            mycursor.execute(sql_acompanhamentos, (id_pedido,))
            acompanhamentos = [row[0] for row in mycursor.fetchall()]
            pedidos[id_cliente]['pedidos'][id_pedido]['acompanhamentos'] = acompanhamentos  # Adiciona os acompanhamentos ao pedido

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