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
    
   
    def inserir_produto_carrinho(self, cod_produto, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"INSERT INTO tb_carrinho (id_cliente, cod_produto) VALUES ('{id_cliente}', '{cod_produto}')"

        mycursor.execute(sql)
        mydb.commit()
        mydb.close()
        return True
    
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
    
    def exibir_carrinho(self, id_cliente):
        mydb =  Conexao.conectar()
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

        for resultado in resultado1:
            lista_carrinho.append({
                'nome_produto': resultado[1],
                'preco': resultado[2],
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[6]
        })
        mydb.close()
        return lista_carrinho
    
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

        sql = f"INSERT INTO tb_pedidos (id_cliente, data_pedido, status) VALUES ('{id_cliente}', CURDATE(), 'Pendente')"

        mycursor.execute(sql)
        mydb.commit()
        mydb.close()
        return True




    def exibir_pedidos(self, id_cliente):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"""
            SELECT p.id_pedido, cl.nome_comp, cl.telefone, pr.nome_produto, pr.preco, p.data_pedido, p.status
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_carrinho c ON cl.id_cliente = c.id_cliente
            JOIN tb_produto pr ON c.cod_produto = pr.cod_produto
            group by cl.id_cliente
        """

        mycursor.execute(sql)
        resultado = mycursor.fetchall()
    
        lista_pedidos = []

        for resultado in resultado:
            lista_pedidos.append({
                'id_pedido': resultado[0],
                'nome_cliente': resultado[1],
                'telefone': resultado[2],
                'nome_produto': resultado[3],
                'preco': resultado[4],
                'data_pedido': resultado[5],
                'status': resultado[6]
                })
            
        # sql_remover = f"DELETE FROM tb_carrinho WHERE '{id_cliente}'"

        # mycursor.execute(sql_remover)
        # mydb.commit()
        mydb.close()
        return lista_pedidos