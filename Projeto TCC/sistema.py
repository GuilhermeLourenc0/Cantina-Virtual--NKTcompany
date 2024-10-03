from conexao import Conexao
from hashlib import sha256

class Sistema:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


    def exibir_produtos_adm(self):
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
                'id_produto': produto[0],
                'habilitado': produto[6]  # Certifique-se de que este índice corresponde ao campo 'habilitado'
            })
        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_produtos if lista_produtos else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado

    def exibir_produtos(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar apenas produtos habilitados (assumindo coluna 'habilitado')
        sql = "SELECT * FROM tb_produto WHERE habilitado = 1"
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





    # Modifique a função para desabilitar produto
    def desabilitar_produto_adm(self, produto_id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Atualizar o status do produto para desabilitado (0)
        sql = "UPDATE tb_produto SET habilitado = 0 WHERE cod_produto = %s"
        mycursor.execute(sql, (produto_id,))

        mydb.commit()
        mydb.close()

        return {"message": "Produto desabilitado com sucesso!"}  # Retorna um dicionário


    # Modifique a função para habilitar produto
    def habilitar_produto_adm(self, produto_id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Atualizar o status do produto para habilitado (1)
        sql = "UPDATE tb_produto SET habilitado = 1 WHERE cod_produto = %s"
        mycursor.execute(sql, (produto_id,))

        mydb.commit()
        mydb.close()

        return {"message": "Produto habilitado com sucesso!"}  # Retorna um dicionário


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




    # Método para exibir todos os pedidos de um cliente específico com detalhes dos produtos
    def exibir_historico(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter todos os pedidos do cliente específico com detalhes dos produtos
        sql = """
            SELECT p.id_pedido, cl.id_cliente, cl.nome_comp, cl.telefone, 
                pr.nome_produto, pr.preco, pp.quantidade, 
                p.data_pedido, p.status
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            WHERE cl.id_cliente = %s  -- Filtra pelos pedidos do cliente específico
            ORDER BY p.data_pedido DESC, pr.nome_produto
        """
        mycursor.execute(sql, (id_cliente,))
        resultados = mycursor.fetchall()

        pedidos = {}

        # Itera sobre os resultados e organiza as informações de pedidos
        for resultado in resultados:
            id_pedido = resultado[0]
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
                    'total_preco': 0  # Inicializa o total do pedido
                }

            # Adiciona o produto ao pedido e calcula o total
            total_produto = preco_produto * quantidade_produto
            pedidos[id_cliente]['pedidos'][id_pedido]['produtos'].append({
                'nome_produto': nome_produto,
                'preco': preco_produto,
                'quantidade': quantidade_produto
            })
            pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += total_produto  # Atualiza o total do pedido

        mydb.close()
        return pedidos


    def atualizar_produto(self, id_produto, nome, preco, descricao, file=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Monta a consulta SQL para atualizar o produto
        sql = """
            UPDATE tb_produto
            SET nome_produto = %s, preco = %s, descricao = %s
        """
        valores = (nome, preco, descricao)

        # Se um arquivo foi enviado
        if file:
            # Lê os dados da imagem como binário
            dados_imagem = file.read()
            sql += ", imagem_binaria = %s, url_img = %s"  # Atualiza a coluna da imagem
            valores += (dados_imagem, f"/imagem_produto/{id_produto}")  # Adiciona a URL da imagem aos valores

        sql += " WHERE cod_produto = %s"  # Condição para o ID do produto
        valores += (id_produto,)  # Adiciona o ID do produto aos valores

        # Executa a consulta
        mycursor.execute(sql, valores)

        mydb.commit()
        mydb.close()



    def obter_imagem_produto(self, cod_produto):
            mydb = Conexao.conectar()
            mycursor = mydb.cursor()

            # Consulta SQL paa robter a imagem do produto
            sql = "SELECT imagem_binaria FROM tb_produto WHERE cod_produto = %s"
            mycursor.execute(sql, (cod_produto,))
            resultado = mycursor.fetchone()

            mydb.close()

            if resultado:
                return resultado[0]  # Retorna a imagem binária
            return None  # Retorna None se não encontrar


    def perfil_senha(self, id_cliente):
            mydb = Conexao.conectar()
            mycursor = mydb.cursor()

            # Consulta SQL paa robter a imagem do produto
            sql = "SELECT senha FROM tb_cliente WHERE id_cliente = %s"
            mycursor.execute(sql, (id_cliente,))
            resultado = mycursor.fetchone()


    def atualizar_status_pedido(self, id_pedido, novo_status):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            # Atualiza o status do pedido
            sql = "UPDATE tb_pedidos SET status = %s WHERE id_pedido = %s"
            mycursor.execute(sql, (novo_status, id_pedido))

            mydb.commit()  # Confirma a alteração
            return {"message": "Status atualizado com sucesso!"}  # Retorna mensagem de sucesso
        except Exception as e:
            mydb.rollback()  # Reverte a transação em caso de erro
            return {"error": f"Erro ao atualizar o status: {str(e)}"}
        finally:
            mydb.close()  # Fecha a conexão com o banco de dados



    def cancelar_pedido(self, id_pedido):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            # Atualiza o status do pedido para 'Cancelado'
            sql = "UPDATE tb_pedidos SET status = 'Cancelado' WHERE id_pedido = %s"
            mycursor.execute(sql, (id_pedido,))

            mydb.commit()  # Confirma a alteração
            return {"message": "Pedido cancelado com sucesso!"}  # Retorna mensagem de sucesso
        except Exception as e:
            mydb.rollback()  # Reverte a transação em caso de erro
            return {"error": f"Erro ao cancelar o pedido: {str(e)}"}
        finally:
            mydb.close()  # Fecha a conexão com o banco de dados



    def obter_perfil(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()
        
        try:
            mycursor.execute("SELECT nome_comp, imagem_binaria FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            perfil = mycursor.fetchone()
            return perfil  # Retorna uma tupla (nome, imagem) ou None se não encontrado
        except Exception as e:
            return None  # Lida com qualquer erro
        finally:
            mycursor.close()
            mydb.close()


    def obter_imagem_perfil(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("SELECT imagem_binaria FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            imagem = mycursor.fetchone()
            return imagem[0] if imagem else None
        except Exception as e:
            return None
        finally:
            mycursor.close()
            mydb.close()



    def atualizar_perfil(self, id_cliente, nome, senha_confirmacao, caminho_imagem=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            # Verifica se a senha está correta (mas não atualiza)
            mycursor.execute("SELECT senha FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            senha_atual = mycursor.fetchone()

            if senha_atual is None or senha_atual[0] != senha_confirmacao:
                return {"error": "Senha incorreta. Não foi possível atualizar o perfil."}

            # Atualiza apenas o nome e a imagem, sem mudar a senha
            sql = "UPDATE tb_cliente SET nome_comp = %s"
            valores = [nome]

            # Verifica se o cliente já possui uma imagem
            mycursor.execute("SELECT imagem_binaria FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            imagem_existente = mycursor.fetchone()

            if caminho_imagem:
                with open(caminho_imagem, 'rb') as imagem:
                    dados_imagem = imagem.read()
                # Se já existe uma imagem, atualiza. Caso contrário, adiciona a nova imagem.
                if imagem_existente[0] is not None:
                    sql += ", imagem_binaria = %s"
                    valores.append(dados_imagem)
                else:
                    sql += ", imagem_binaria = %s"
                    valores.append(dados_imagem)

            sql += " WHERE id_cliente = %s"
            valores.append(id_cliente)

            mycursor.execute(sql, valores)
            mydb.commit()

            return {"message": "Perfil atualizado com sucesso!"}
        
        except Exception as e:
            mydb.rollback()
            return {"error": f"Erro ao atualizar o perfil: {str(e)}"}
        
        finally:
            mycursor.close()  # Fecha o cursor
            mydb.close()  # Fecha a conexão com o banco de dados






    def verificar_senha(self, id_cliente, senha_fornecida):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            senha_fornecida = sha256(senha_fornecida.encode()).hexdigest()
            # Busca a senha atual do cliente no banco de dados
            mycursor.execute("SELECT senha FROM tb_cliente WHERE id_cliente = %s", (id_cliente,))
            senha_armazenada = mycursor.fetchone()

            if senha_armazenada is None:
                return False  # Se o cliente não for encontrado

            # Verifica se a senha fornecida é igual à senha armazenada
            return senha_armazenada[0] == senha_fornecida  # Retorna True ou False

        except Exception as e:
            return {"error": f"Erro ao verificar a senha: {str(e)}"}

        finally:
            mycursor.close()  # Fecha o cursor
            mydb.close()  # Fecha a conexão com o banco de dados

