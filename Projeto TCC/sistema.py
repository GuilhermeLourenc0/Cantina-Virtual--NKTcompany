from conexao import Conexao


class Sistema:
    def __init__(self):
        self.tel = None
        self.id_produto = None

    # def filtro(self, filtro):
    #     mydb =  Conexao.conectar()
    #     mycursor = mydb.cursor()

    #     sql = f"SELECT * from tb_produtos where categoria = '{filtro}'"

    #     mycursor.execute(sql)
    #     resultado = mycursor.fetchall()
       
    #     lista_filtro = []

    #     for filtro in resultado:
    #         lista_filtro.append({
    #             'nome_produto': filtro[1],
    #             'preco': filtro[2],
    #             'imagem_produto': filtro[3],
    #             'descricao': filtro[5],
    #             'id_produto': filtro[0]       
    #     })
    #     mydb.close()
    #     if lista_filtro:
    #         return lista_filtro
    #     else:
    #         return []
        
    

    def exibir_produtos(self):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"SELECT * from tb_produto"
        mycursor.execute(sql)
        
        resultado = mycursor.fetchall()
       
        lista_produtos = []

        for produto in resultado:
            lista_produtos.append({
                'nome_produto': produto[1],
                'preco': produto[2],
                'imagem_produto': produto[3],
                'categoria': produto[5],
                'descricao': produto[4],
                'id_produto': produto[0] 
            })
        mydb.close()
        if lista_produtos:
            return lista_produtos 
        else:
            return []
    
    def exibir_produto(self, id):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"SELECT * from tb_produto where cod_produto = '{id}'"

        mycursor.execute(sql)
        resultado = mycursor.fetchone()

        dicionario_produto = {
            'nome_produto': resultado[1],
            'preco': resultado[2],
            'imagem_produto': resultado[3],
            'descricao': resultado[4],
            'cod_produto': resultado[0]            
        }

        lista = []

        lista.append(dicionario_produto)

        mydb.commit()
        mydb.close()
        return lista

    def inserir_produto_carrinho(self, cod_produto, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Verifica se o produto já está no carrinho do cliente
        sql_verificar = f"""
            SELECT quantidade FROM tb_carrinho
            WHERE id_cliente = '{id_cliente}' AND cod_produto = '{cod_produto}'
        """
        mycursor.execute(sql_verificar)
        resultado = mycursor.fetchone()

        if resultado:
            # Se o produto já estiver no carrinho, aumenta a quantidade
            nova_quantidade = resultado[0] + 1
            sql_update = f"""
                UPDATE tb_carrinho
                SET quantidade = '{nova_quantidade}'
                WHERE id_cliente = '{id_cliente}' AND cod_produto = '{cod_produto}'
            """
            mycursor.execute(sql_update)
        else:
            # Se o produto não estiver no carrinho, insere um novo item
            sql_inserir = f"""
                INSERT INTO tb_carrinho (id_cliente, cod_produto, quantidade)
                VALUES ('{id_cliente}', '{cod_produto}', 1)
            """
            mycursor.execute(sql_inserir)

        mydb.commit()
        mydb.close()
        return True
        

    
    def exibir_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"""
                SELECT p.cod_produto, p.nome_produto, p.preco, p.url_img, p.id_categoria, p.descricao, c.id_carrinho
                FROM tb_carrinho AS c
                JOIN tb_produto AS p ON c.cod_produto = p.cod_produto
                WHERE c.id_cliente = '{id_cliente}';
            """

        mycursor.execute(sql)
        resultado1 = mycursor.fetchall()
    
        lista_carrinho = []
        total_preco = 0  # Inicializa o total de preço

        for resultado in resultado1:
            preco_produto = resultado[2]
            quantidade_produto = 1  # Assumindo uma quantidade padrão de 1 para cada produto no carrinho

            lista_carrinho.append({
                'nome_produto': resultado[1],
                'preco': preco_produto,
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[6]
            })

            total_preco += preco_produto * quantidade_produto  # Atualiza o total de preço

        mydb.close()

        # Formata o total de preço como uma string com duas casas decimais
        total_preco_formatado = "{:.2f}".format(total_preco)

        return {
            'produtos': lista_carrinho,
            'total_preco': total_preco_formatado
        }

        
    
    def excluir_produto(self, btn_excluir):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"DELETE FROM tb_carrinho WHERE id_carrinho = '{btn_excluir}'"

        mycursor.execute(sql)
        mydb.commit()
        mydb.close()




    def enviar_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # 1. Inserir o pedido na tabela `tb_pedidos`
        sql_pedido = f"INSERT INTO tb_pedidos (id_cliente, data_pedido, status) VALUES (%s, CURDATE(), 'Pendente')"
        mycursor.execute(sql_pedido, (id_cliente,))
        id_pedido = mycursor.lastrowid  # Pega o ID do pedido recém-criado

        # 2. Buscar os itens no carrinho do cliente
        sql_carrinho = f"SELECT cod_produto, quantidade FROM tb_carrinho WHERE id_cliente = %s"
        mycursor.execute(sql_carrinho, (id_cliente,))
        itens_carrinho = mycursor.fetchall()

        # 3. Inserir os produtos na tabela `tb_produtos_pedidos`
        for item in itens_carrinho:
            cod_produto = item[0]
            quantidade = item[1]
            sql_produtos_pedido = f"INSERT INTO tb_produtos_pedidos (id_pedido, cod_produto, quantidade) VALUES (%s, %s, %s)"
            mycursor.execute(sql_produtos_pedido, (id_pedido, cod_produto, quantidade))

        # 4. Remover os itens do carrinho após finalizar o pedido
        sql_limpar_carrinho = f"DELETE FROM tb_carrinho WHERE id_cliente = %s"
        mycursor.execute(sql_limpar_carrinho, (id_cliente,))

        # Confirmar as alterações
        mydb.commit()
        mydb.close()
        return True




    def exibir_pedidos(self):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

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

        # Itera sobre os resultados da consulta
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
                    'total_preco': 0  # Inicializa o total de preço para o pedido
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