from conexao import Conexao
from hashlib import sha256

class Carrinho:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


    # Método para inserir um item (produto ou marmita) no carrinho de um cliente
    def inserir_item_carrinho(self, id_item, tipo_item, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Verifica se o item já está no carrinho do cliente
        sql_verificar = """
            SELECT quantidade FROM tb_carrinho
            WHERE id_cliente = %s AND id_item = %s AND tipo_item = %s
        """
        mycursor.execute(sql_verificar, (id_cliente, id_item, tipo_item))
        resultado = mycursor.fetchone()

        if resultado:
            # Se o item já estiver no carrinho, atualiza a quantidade
            nova_quantidade = resultado[0] + 1
            sql_update = """
                UPDATE tb_carrinho
                SET quantidade = %s
                WHERE id_cliente = %s AND id_item = %s AND tipo_item = %s
            """
            mycursor.execute(sql_update, (nova_quantidade, id_cliente, id_item, tipo_item))
        else:
            # Se o item não estiver no carrinho, insere um novo item
            sql_inserir = """
                INSERT INTO tb_carrinho (id_cliente, id_item, tipo_item, quantidade)
                VALUES (%s, %s, %s, 1)
            """
            mycursor.execute(sql_inserir, (id_cliente, id_item, tipo_item))

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


    # Método para atualizar a quantidade de um produto específico no carrinho
    def atualizar_quantidade_produto_carrinho(self, id_carrinho, quantidade):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para atualizar a quantidade do produto no carrinho
        sql = "UPDATE tb_carrinho SET quantidade = %s WHERE id_carrinho = %s"
        mycursor.execute(sql, (quantidade, id_carrinho))

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