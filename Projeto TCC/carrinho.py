from conexao import Conexao

class Carrinho:
    def adicionar_ao_carrinho(id_cliente, cod_produto):
        """Adiciona um produto ao carrinho do cliente."""
        conexao = Conexao.conectar()
        cursor = conexao.cursor()

        sql = "INSERT INTO tb_carrinho (id_cliente, cod_produto) VALUES (%s, %s)"
        valores = (id_cliente, cod_produto)

        cursor.execute(sql, valores)
        conexao.commit()

        cursor.close()
        conexao.close()
        
    def obter_carrinho(id_cliente):
        conexao = Conexao.conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
        SELECT p.cod_produto, p.nome_produto, p.categoria, format(p.preco, 2, 'pt_BR') as preco
        FROM tb_carrinho c
        JOIN tb_produtos p ON c.cod_produto = p.cod_produto ON
        WHERE c.id_cliente = %s
        """
        cursor.execute(sql, (id_cliente,))
        produtos = cursor.fetchall()
        print(produtos)

        cursor.close()
        conexao.close()

        return produtos
    

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