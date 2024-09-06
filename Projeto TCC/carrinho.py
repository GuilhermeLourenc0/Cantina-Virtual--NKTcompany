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