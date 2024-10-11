from conexao import Conexao
from hashlib import sha256

class Adm:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


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






    

    # ========================== desabilitar / habilitar produto ===================================
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
    



    # Modifique a função para desabilitar marmita
    def desabilitar_marmita_adm(self, marmita_id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Atualizar o status da marmita para desabilitado (0)
        sql = "UPDATE tb_marmita SET habilitado = 0 WHERE id_marmita = %s"
        mycursor.execute(sql, (marmita_id,))

        mydb.commit()
        mydb.close()

        return {"message": "Marmita desabilitada com sucesso!"}  # Retorna um dicionário


    # Modifique a função para habilitar marmita
    def habilitar_marmita_adm(self, marmita_id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Atualizar o status da marmita para habilitado (1)
        sql = "UPDATE tb_marmita SET habilitado = 1 WHERE id_marmita = %s"
        mycursor.execute(sql, (marmita_id,))

        mydb.commit()
        mydb.close()

        return {"message": "Marmita habilitada com sucesso!"}  # Retorna um dicionário


    


    # ====================== Inserir Produtos =========================
    def inserir_produto(self, nomeP, preco, imagem, descricao, categoria, guarnicoes_novas=[]):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para inserir o produto na tabela `tb_produto`
        sql = f"INSERT INTO tb_produto (nome_produto, preco, url_img, descricao, id_categoria) VALUES ('{nomeP}', {preco}, '{imagem}', '{descricao}', {categoria})"
        mycursor.execute(sql)

        # Captura o ID do produto recém-inserido para associar guarnições
        id_produto = mycursor.lastrowid

        # Inserir novas guarnições se existirem
        for nova_guarnicao in guarnicoes_novas:
            self.inserir_guarnicao(nova_guarnicao)

            # Associar a nova guarnição ao produto
            sql_associacao = "INSERT INTO tb_produto_guarnicao (id_produto, id_guarnicao) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_produto, nova_guarnicao))

        mydb.commit()  # Confirma as alterações no banco de dados
        mydb.close()  # Fecha a conexão
        return True

    
    def inserir_marmita(self, nomeP, preco, imagem, descricao, tamanho, guarnicoes_novas=[]):
        """
        Insere uma nova marmita no sistema, associando-a à categoria correta. As informações da marmita
        incluem nome, preço, URL da imagem, descrição, tamanho e as guarnições associadas.
        
        Parâmetros:
        - nomeP: nome da marmita.
        - preco: preço da marmita.
        - imagem: URL da imagem da marmita.
        - descricao: breve descrição da marmita.
        - tamanho: tamanho da marmita (Pequena, Média, Grande).
        - guarnicoes_novas: lista de novas guarnições a serem inseridas.
        
        Retorno:
        - Retorna True se a marmita for inserida com sucesso, ou False em caso de erro.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para inserir a marmita na tabela `tb_marmita`
        sql = f"""
        INSERT INTO tb_marmita (nome_marmita, preco, url_img, descricao, tamanho)
        VALUES ('{nomeP}', {preco}, '{imagem}', '{descricao}', '{tamanho}')
        """
        mycursor.execute(sql)
        
        # Captura o ID da marmita recém-inserida para associar guarnições
        id_marmita = mycursor.lastrowid

        # Inserir novas guarnições se existirem
        for nova_guarnicao in guarnicoes_novas:
            self.inserir_guarnicao(nova_guarnicao)

            # Associar a nova guarnição à marmita (supondo que você tenha uma tabela de associação)
            sql_associacao = "INSERT INTO tb_marmita_guarnicao (id_marmita, id_guarnicao) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_marmita, nova_guarnicao))

        mydb.commit()  # Confirma as alterações no banco de dados
        mydb.close()  # Fecha a conexão
        return True




    def exibir_guarnição(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()
        # Query SQL para inserir o produto na tabela `tb_produto`
        sql = f"SELECT * FROM tb_guarnicao"
        mycursor.execute(sql)
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        lista_guarnicao = []

        # Itera sobre os resultados e adiciona cada produto à lista
        for produto in resultado:
            lista_guarnicao.append({
                'nome_guarnicao': produto[1],
                'id_guarnicao': produto[0]
            })

        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_guarnicao if lista_guarnicao else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado



    def inserir_guarnicao(self, nome_guarnicao):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para inserir a nova guarnição
        sql = "INSERT INTO tb_guarnicao (nome_guarnicao) VALUES (%s)"
        mycursor.execute(sql, (nome_guarnicao,))

        mydb.commit()  # Confirma as alterações no banco de dados
        id_guarnicao = mycursor.lastrowid  # Captura o ID da nova guarnição
        mydb.close()  # Fecha a conexão
        return True, id_guarnicao  # Retorna True e o ID





    def exibir_categorias(self):
        """
        Retorna uma lista com todas as categorias de produtos disponíveis, consultando a tabela `tb_categoria`.
        Cada categoria contém o ID da categoria e o nome da categoria.
        
        Retorno:
        - Uma lista de dicionários, onde cada dicionário representa uma categoria com 'id_categoria' e 'nome'.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Query SQL para selecionar todas as categorias
        sql = "SELECT * from tb_categoria"
        mycursor.execute(sql)

        # Obtém os resultados e os organiza em uma lista
        resultado = mycursor.fetchall()
        lista_categorias = [{'id_categoria': categoria[0], 'nome': categoria[1]} for categoria in resultado]

        mydb.commit()
        mydb.close()
        return lista_categorias 
    

    # ============================ Editar Prduto ==============================
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
