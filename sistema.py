from conexao import Conexao


class Sistema:
    def __init__(self):
        self.cpf = None
        self.id_produto = None

    def filtro(self, filtro):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"SELECT * from tb_produtos where categoria = '{filtro}'"

        mycursor.execute(sql)
        resultado = mycursor.fetchall()
       
        lista_filtro = []

        for filtro in resultado:
            lista_filtro.append({
                'nome_produto': filtro[1],
                'preco': filtro[2],
                'imagem_produto': filtro[3],
                'descricao': filtro[5],
                'id_produto': filtro[0]       
        })
        mydb.close()
        if lista_filtro:
            return lista_filtro
        else:
            return []
        
    

    def exibir_produtos(self):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"SELECT * from tb_produtos"
        mycursor.execute(sql)
        
        resultado = mycursor.fetchall()
       
        lista_categorias = []

        for categoria in resultado:
            lista_categorias.append({
                'nome_produto': categoria[1],
                'preco': categoria[2],
                'imagem_produto': categoria[3],
                'categoria': categoria[4],
                'descricao': categoria[5],
                'id_produto': categoria[0] 
            })
        mydb.close()
        if lista_categorias:
            return lista_categorias 
        else:
            return []
    
   
    def inserir_produto_carrinho(self, id_produto, cpf):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"INSERT INTO tb_carrinho (cpf_cliente, id_produto) VALUES ('{cpf}', '{id_produto}')"
        
        mycursor.execute(sql)
        mydb.commit()
        mydb.close()
        return True
    
    def exibir_produto(self, id):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"SELECT * from tb_produtos where id_produto = '{id}'"

        mycursor.execute(sql)
        resultado = mycursor.fetchone()

        dicionario_produto = {
            'nome_produto': resultado[1],
            'preco': resultado[2],
            'imagem_produto': resultado[3],
            'descricao': resultado[5],
            'id_produto': resultado[0]            
        }

        lista = []

        lista.append(dicionario_produto)

        mydb.commit()
        mydb.close()
        return lista
    
    def exibir_carrinho(self, cpf):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"""
                SELECT p.id_produto, p.nome_produto, p.preco, p.imagem_produto, p.categoria, p.descricao, c.id_carrinho
                FROM tb_carrinho AS c
                JOIN tb_produtos AS p ON c.id_produto = p.id_produto
                WHERE c.cpf_cliente = '{cpf}';
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

    def exibir_produto1(self, id):
            mydb =  Conexao.conectar()
            mycursor = mydb.cursor()

            sql = f"SELECT * FROM tb_produtos INNER JOIN tb_produtos WHERE id_produto = '{id}'"

            mycursor.execute(sql)
            resultado = mycursor.fetchall()
        
            lista_produto1 = []

            for id_produto in resultado:
                lista_produto1.append({
                    'nome_produto': id_produto[1],
                    'preco': id_produto[2],
                    'imagem_produto': id_produto[3],
                    'descricao': id_produto[5]            
            })

            mydb.close()

    def inserir_comentario(self, comentario, nome_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"INSERT INTO tb_comentario (comentario_usuario, nome_usuario) VALUES ('{comentario}', '{nome_cliente}')"

        
        mycursor.execute(sql)
        mydb.commit()
        mydb.close()
        return True
    
    def exibir_comentario(self, nome_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()
        
        sql = f"SELECT comentario_usuario FROM tb_comentario WHERE nome_usuario = '{nome_cliente}'"
        mycursor.execute(sql)
        resultado = mycursor.fetchall()
        
        lista_comentario = []

        for comentario in resultado:
            lista_comentario.append({
                'comentario': comentario[0]  # Assumindo que o comentário está na primeira coluna (índice 0)
            })

        mydb.close()
        return lista_comentario
    
    def excluir_produto(self, btn_excluir):
        mydb =  Conexao.conectar()
        mycursor = mydb.cursor()

        sql = f"DELETE FROM tb_carrinho WHERE id_carrinho = '{btn_excluir}'"

        mycursor.execute(sql)
        mydb.commit()
        mydb.close()
        