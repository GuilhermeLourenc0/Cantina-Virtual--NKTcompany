from conexao import Conexao

class Sistema:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None

    # Método para exibir todos os produtos disponíveis
    def exibir_produtos(self):
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

    # Método para inserir um produto no carrinho de um cliente
    def inserir_produto_carrinho(self, cod_produto, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Verifica se o produto já está no carrinho do cliente
        sql_verificar = """
            SELECT quantidade FROM tb_carrinho
            WHERE id_cliente = %s AND cod_produto = %s
        """
        mycursor.execute(sql_verificar, (id_cliente, cod_produto))
        resultado = mycursor.fetchone()

        if resultado:
            # Se o produto já estiver no carrinho, atualiza a quantidade
            nova_quantidade = resultado[0] + 1
            sql_update = """
                UPDATE tb_carrinho
                SET quantidade = %s
                WHERE id_cliente = %s AND cod_produto = %s
            """
            mycursor.execute(sql_update, (nova_quantidade, id_cliente, cod_produto))
        else:
            # Se o produto não estiver no carrinho, insere um novo item
            sql_inserir = """
                INSERT INTO tb_carrinho (id_cliente, cod_produto, quantidade)
                VALUES (%s, %s, 1)
            """
            mycursor.execute(sql_inserir, (id_cliente, cod_produto))

        mydb.commit()
        mydb.close()
        return True

    # Método para exibir os produtos no carrinho de um cliente
    def exibir_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter produtos no carrinho e suas quantidades
        sql = """
            SELECT p.cod_produto, p.nome_produto, p.preco, p.url_img, p.id_categoria, p.descricao, c.id_carrinho, c.quantidade
            FROM tb_carrinho AS c
            JOIN tb_produto AS p ON c.cod_produto = p.cod_produto
            WHERE c.id_cliente = %s;
        """
        mycursor.execute(sql, (id_cliente,))
        resultado1 = mycursor.fetchall()

        lista_carrinho = []
        total_preco = 0  # Inicializa o total de preço

        # Itera sobre os resultados e adiciona os produtos ao carrinho
        for resultado in resultado1:
            preco_produto = resultado[2]
            quantidade_produto = resultado[7]

            lista_carrinho.append({
                'nome_produto': resultado[1],
                'preco': preco_produto,
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[6],
                'quantidade': quantidade_produto
            })

            total_preco += preco_produto * quantidade_produto  # Atualiza o total de preço

        mydb.close()
        total_preco_formatado = "{:.2f}".format(total_preco)  # Formata o total de preço
        return {
            'produtos': lista_carrinho,
            'total_preco': total_preco_formatado
        }




    # Método para excluir um produto do carrinho
    def remover_produto_carrinho(self, id_carrinho):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para remover o produto do carrinho
        sql = "DELETE FROM tb_carrinho WHERE id_carrinho = %s"
        mycursor.execute(sql, (id_carrinho,))

        mydb.commit()
        mydb.close()





    def excluir_produto_adm(self, btn_excluir):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para remover um produto do carrinho
        sql = "DELETE FROM tb_produto WHERE cod_produto = %s"
        mycursor.execute(sql, (btn_excluir,))

        mydb.commit()
        mydb.close()

    # Método para enviar o conteúdo do carrinho como um pedido
    def enviar_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # 1. Insere um novo pedido na tabela `tb_pedidos`
        sql_pedido = "INSERT INTO tb_pedidos (id_cliente, data_pedido, status) VALUES (%s, CURDATE(), 'Pendente')"
        mycursor.execute(sql_pedido, (id_cliente,))
        id_pedido = mycursor.lastrowid  # Obtém o ID do novo pedido

        # 2. Obtém os itens do carrinho
        sql_carrinho = "SELECT cod_produto, quantidade FROM tb_carrinho WHERE id_cliente = %s"
        mycursor.execute(sql_carrinho, (id_cliente,))
        itens_carrinho = mycursor.fetchall()

        # 3. Insere os produtos do carrinho na tabela `tb_produtos_pedidos`
        for item in itens_carrinho:
            cod_produto = item[0]
            quantidade = item[1]
            sql_produtos_pedido = "INSERT INTO tb_produtos_pedidos (id_pedido, cod_produto, quantidade) VALUES (%s, %s, %s)"
            mycursor.execute(sql_produtos_pedido, (id_pedido, cod_produto, quantidade))

        # 4. Remove os itens do carrinho após finalizar o pedido
        sql_limpar_carrinho = "DELETE FROM tb_carrinho WHERE id_cliente = %s"
        mycursor.execute(sql_limpar_carrinho, (id_cliente,))

        mydb.commit()
        mydb.close()
        return True

    # Método para exibir todos os pedidos com detalhes dos produtos
    def exibir_pedidos(self):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter todos os pedidos com detalhes dos produtos
        sql = """
            SELECT p.id_pedido, cl.id_cliente, cl.nome_comp, cl.telefone, pr.nome_produto, pr.preco, pp.quantidade, p.data_pedido, p.status
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            ORDER BY cl.id_cliente, p.id_pedido, pr.nome_produto
        """
        mycursor.execute(sql)
        resultados = mycursor.fetchall()

        pedidos = {}

        # Itera sobre os resultados e organiza as informações de pedidos
        for resultado in resultados:
            id_pedido = resultado[0]
            id_cliente = resultado[1]
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
                    'total_preco': 0
                }

            # Adiciona o produto ao pedido
            pedidos[id_cliente]['pedidos'][id_pedido]['produtos'].append({
                'nome_produto': nome_produto,
                'preco': preco_produto,
                'quantidade': quantidade_produto
            })

            # Atualiza o total de preço do pedido
            pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += preco_produto * quantidade_produto

        mydb.close()
        return pedidos

    # Método para atualizar a quantidade de um produto específico no carrinho
    def atualizar_quantidade_produto_carrinho(self, id_carrinho, quantidade):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para atualizar a quantidade do produto no carrinho
        sql = "UPDATE tb_carrinho SET quantidade = %s WHERE id_carrinho = %s"
        mycursor.execute(sql, (quantidade, id_carrinho))

        mydb.commit()
        mydb.close()


    def perfil():
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()