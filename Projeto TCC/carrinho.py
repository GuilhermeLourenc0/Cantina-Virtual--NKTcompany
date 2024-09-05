from conexao import Conexao

class Carrinho:
    def adicionar_ao_carrinho(telefone, cod_prod):
        """Adiciona um produto ao carrinho do cliente."""
        conexao = Conexao.conectar()
        cursor = conexao.cursor()

        sql = "INSERT INTO tb_carrinho (telefone, cod_prod) VALUES (%s, %s)"
        valores = (telefone, cod_prod)

        cursor.execute(sql, valores)
        conexao.commit()

        cursor.close()
        conexao.close()
        
    def obter_carrinho(telefone):
        conexao = Conexao.conectar()
        cursor = conexao.cursor(dictionary=True)

        sql = """
        SELECT p.cod_prod, p.nome_produto, p.categoria, format(p.preco, 2, 'pt_BR') as preco, 
               p.descricao, f.foto_0
        FROM tb_carrinho c
        JOIN tb_produtos p ON c.cod_prod = p.cod_prod ON
        WHERE c.telefone = %s
        """
        cursor.execute(sql, (telefone,))
        produtos = cursor.fetchall()
        print(produtos)

        cursor.close()
        conexao.close()

        return produtos