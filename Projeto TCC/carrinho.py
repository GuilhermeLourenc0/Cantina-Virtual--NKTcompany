from conexao import Conexao
from hashlib import sha256

class Carrinho:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


      # Função para inserir itens no carrinho
    def inserir_item_carrinho(self, id_item, id_cliente, tipo_item):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        if tipo_item == 'produto':
            # Verifica se o produto já está no carrinho do cliente
            sql_verificar = """
                SELECT quantidade FROM tb_carrinho
                WHERE cod_produto = %s AND id_cliente = %s
            """
            mycursor.execute(sql_verificar, (id_item, id_cliente))
        elif tipo_item == 'marmita':
            # Verifica se a marmita já está no carrinho do cliente
            sql_verificar = """
                SELECT quantidade FROM tb_carrinho
                WHERE id_marmita = %s AND id_cliente = %s
            """
            mycursor.execute(sql_verificar, (id_item, id_cliente))

        resultado = mycursor.fetchone()

        if resultado:
            nova_quantidade = resultado[0] + 1
            if tipo_item == 'produto':
                sql_update = """
                    UPDATE tb_carrinho
                    SET quantidade = %s
                    WHERE cod_produto = %s AND id_cliente = %s
                """
                mycursor.execute(sql_update, (nova_quantidade, id_item, id_cliente))
            elif tipo_item == 'marmita':
                sql_update = """
                    UPDATE tb_carrinho
                    SET quantidade = %s
                    WHERE id_marmita = %s AND id_cliente = %s
                """
                mycursor.execute(sql_update, (nova_quantidade, id_item, id_cliente))
        else:
            if tipo_item == 'produto':
                sql_inserir = """
                    INSERT INTO tb_carrinho (id_cliente, cod_produto, quantidade, tipo_item)
                    VALUES (%s, %s, 1, 'produto')
                """
                mycursor.execute(sql_inserir, (id_cliente, id_item))
            elif tipo_item == 'marmita':
                sql_inserir = """
                    INSERT INTO tb_carrinho (id_cliente, id_marmita, quantidade, tipo_item)
                    VALUES (%s, %s, 1, 'marmita')
                """
                mycursor.execute(sql_inserir, (id_cliente, id_item))

        mydb.commit()
        mydb.close()
        return True



   # Método para exibir os itens no carrinho de um cliente
    def exibir_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter produtos no carrinho e suas quantidades
        sql_produtos = """
            SELECT p.cod_produto, p.nome_produto, p.preco, p.url_img, p.id_categoria, p.descricao, c.id_carrinho, c.quantidade
            FROM tb_carrinho AS c
            JOIN tb_produto AS p ON c.cod_produto = p.cod_produto
            WHERE c.id_cliente = %s AND c.tipo_item = 'produto';
        """
        mycursor.execute(sql_produtos, (id_cliente,))
        resultado_produtos = mycursor.fetchall()

        # Consulta SQL para obter marmitas no carrinho e suas quantidades
        sql_marmitas = """
            SELECT m.id_marmita, m.nome_marmita, m.preco, m.url_img, c.id_carrinho, c.quantidade
            FROM tb_carrinho AS c
            JOIN tb_marmita AS m ON c.id_marmita = m.id_marmita
            WHERE c.id_cliente = %s AND c.tipo_item = 'marmita';
        """
        mycursor.execute(sql_marmitas, (id_cliente,))
        resultado_marmitas = mycursor.fetchall()

        lista_carrinho = []
        total_preco = 0  # Inicializa o total de preço

        # Itera sobre os resultados de produtos e adiciona ao carrinho
        for resultado in resultado_produtos:
            preco_produto = resultado[2]
            quantidade_produto = resultado[7]

            lista_carrinho.append({
                'nome_produto': resultado[1],
                'preco': preco_produto,
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[6],
                'quantidade': quantidade_produto,
                'tipo': 'produto'  # Adiciona o tipo
            })

            total_preco += preco_produto * quantidade_produto  # Atualiza o total de preço

        # Itera sobre os resultados de marmitas e adiciona ao carrinho
        for resultado in resultado_marmitas:
            preco_marmita = resultado[2]
            quantidade_marmita = resultado[5]

            lista_carrinho.append({
                'nome_produto': resultado[1],
                'preco': preco_marmita,
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[4],
                'quantidade': quantidade_marmita,
                'tipo': 'marmita'  # Adiciona o tipo
            })

            total_preco += preco_marmita * quantidade_marmita  # Atualiza o total de preço

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


    # Método para atualizar a quantidade de um produto específico no carrinho
    def atualizar_quantidade_produto_carrinho(self, id_carrinho, quantidade):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para atualizar a quantidade do produto no carrinho
        sql = "UPDATE tb_carrinho SET quantidade = %s WHERE id_carrinho = %s"
        mycursor.execute(sql, (quantidade, id_carrinho))

        mydb.commit()
        mydb.close()

    def enviar_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # 1. Insere um novo pedido na tabela `tb_pedidos`
        sql_pedido = "INSERT INTO tb_pedidos (id_cliente, data_pedido, status) VALUES (%s, CURDATE(), 'Pendente')"
        mycursor.execute(sql_pedido, (id_cliente,))
        id_pedido = mycursor.lastrowid  # Obtém o ID do novo pedido

        # 2. Obtém os itens do carrinho (produtos e marmitas)
        sql_carrinho = """
            SELECT 
                CASE WHEN p.cod_produto IS NOT NULL THEN p.cod_produto ELSE m.id_marmita END AS id_item,
                CASE WHEN p.cod_produto IS NOT NULL THEN c.quantidade ELSE m.quantidade END AS quantidade,
                CASE WHEN p.cod_produto IS NOT NULL THEN 'produto' ELSE 'marmita' END AS tipo_item
            FROM tb_carrinho AS c
            LEFT JOIN tb_produto AS p ON c.cod_produto = p.cod_produto
            LEFT JOIN tb_marmita AS m ON c.id_marmita = m.id_marmita
            WHERE c.id_cliente = %s;
        """
        mycursor.execute(sql_carrinho, (id_cliente,))
        itens_carrinho = mycursor.fetchall()

        # 3. Flag para verificar se houve inserção de produtos ou marmitas
        tem_produtos = False
        tem_marmitas = False

        # 4. Insere os produtos e marmitas do carrinho na tabela `tb_produtos_pedidos` e `tb_marmitas_pedidos`
        for item in itens_carrinho:
            cod_item = item[0]
            quantidade = item[1]
            tipo_item = item[2]  # Tipo do item (produto ou marmita)
            
            # Inserção de produtos
            if tipo_item == 'produto' and cod_item is not None:  # Se for um produto
                sql_produtos_pedido = "INSERT INTO tb_produtos_pedidos (id_pedido, cod_produto, quantidade) VALUES (%s, %s, %s)"
                mycursor.execute(sql_produtos_pedido, (id_pedido, cod_item, quantidade))
                tem_produtos = True
            
            # Inserção de marmitas
            elif tipo_item == 'marmita' and cod_item is not None:  # Se for uma marmita
                sql_marmitas_pedido = "INSERT INTO tb_marmitas_pedidos (id_pedido, id_marmita, quantidade) VALUES (%s, %s, %s)"
                mycursor.execute(sql_marmitas_pedido, (id_pedido, cod_item, quantidade))
                tem_marmitas = True

        # 5. Verifica se há produtos ou marmitas antes de finalizar o pedido
        if not tem_produtos and not tem_marmitas:
            mydb.rollback()  # Desfaz a inserção do pedido se não houver itens
            mydb.close()
            return False

        # 6. Remove os itens do carrinho após finalizar o pedido
        sql_limpar_carrinho = "DELETE FROM tb_carrinho WHERE id_cliente = %s"
        mycursor.execute(sql_limpar_carrinho, (id_cliente,))

        mydb.commit()
        mydb.close()
        return True