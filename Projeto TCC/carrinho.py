from conexao import Conexao
from hashlib import sha256

class Carrinho:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


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


    # Método para atualizar a quantidade de um produto específico no carrinho
    def atualizar_quantidade_produto_carrinho(self, id_carrinho, quantidade):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para atualizar a quantidade do produto no carrinho
        sql = "UPDATE tb_carrinho SET quantidade = %s WHERE id_carrinho = %s"
        mycursor.execute(sql, (quantidade, id_carrinho))

        mydb.commit()
        mydb.close()