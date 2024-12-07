from conexao import Conexao
from hashlib import sha256
import os
from datetime import datetime

class Adm:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


    def exibir_pedidos(self):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter os pedidos com detalhes de produtos e marmitas
        sql = """
            SELECT p.id_pedido, cl.id_cliente, cl.nome_comp, cl.telefone, 
                pr.nome_produto, pr.preco AS preco_produto, pp.quantidade, 
                m.nome_marmita, m.preco AS preco_marmita, m.tamanho, m.descricao, 
                p.data_pedido, p.status, p.hora_pedido
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE p.habilitado = 1

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
            nome_marmita = resultado[7]
            preco_marmita = resultado[8]
            tamanho_marmita = resultado[9]
            descricao_marmita = resultado[10]
            data_pedido = resultado[11].strftime('%d/%m/%Y') if resultado[11] else None
            status_pedido = resultado[12]
            hora_pedido = str(resultado[13]) if resultado[13] else None  # Converte hora_pedido para string

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
                    'hora': hora_pedido,  # Usa a hora_pedido já formatada
                    'produtos': [],
                    'marmitas': [],
                    'guarnicoes': [],
                    'acompanhamentos': [],
                    'total_preco': 0
                }

            # Adiciona o produto ao pedido, se houver
            if nome_produto:
                preco_produto_float = float(preco_produto) if preco_produto is not None else 0.0
                pedidos[id_cliente]['pedidos'][id_pedido]['produtos'].append({
                    'nome_produto': nome_produto,
                    'preco': preco_produto_float,
                    'quantidade': quantidade_produto
                })
                pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += preco_produto_float * quantidade_produto

            # Adiciona a marmita ao pedido, se houver
            if nome_marmita:
                preco_marmita_float = float(preco_marmita) if preco_marmita is not None else 0.0
                pedidos[id_cliente]['pedidos'][id_pedido]['marmitas'].append({
                    'nome_marmita': nome_marmita,
                    'preco': preco_marmita_float,
                    'tamanho': tamanho_marmita,
                    'descricao': descricao_marmita,
                    'quantidade': quantidade_produto
                })
                pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += preco_marmita_float * quantidade_produto

        # Buscar guarnições e acompanhamentos para cada pedido
        for id_cliente, dados in pedidos.items():
            for id_pedido in dados['pedidos']:
                # Buscar guarnições
                sql_guarnicoes = """
                    SELECT g.nome_guarnicao 
                    FROM tb_guarnicoes_pedidos AS cg
                    JOIN tb_guarnicao AS g ON cg.guarnicao = g.id_guarnicao
                    WHERE cg.id_pedido = %s
                """
                mycursor.execute(sql_guarnicoes, (id_pedido,))
                guarnicoes = [row[0] for row in mycursor.fetchall()]
                pedidos[id_cliente]['pedidos'][id_pedido]['guarnicoes'] = guarnicoes

                # Buscar acompanhamentos
                sql_acompanhamentos = """
                    SELECT a.nome_acompanhamento 
                    FROM tb_acompanhamentos_pedidos AS ca
                    JOIN tb_acompanhamentos AS a ON ca.acompanhamento = a.id_acompanhamento
                    WHERE ca.id_pedido = %s
                """
                mycursor.execute(sql_acompanhamentos, (id_pedido,))
                acompanhamentos = [row[0] for row in mycursor.fetchall()]
                pedidos[id_cliente]['pedidos'][id_pedido]['acompanhamentos'] = acompanhamentos

        mydb.close()

        # Ordenar pedidos por id_cliente e id_pedido
        pedidos_ordenados = {
            cliente_id: {
                'nome_cliente': dados['nome_cliente'],
                'telefone': dados['telefone'],
                'pedidos': dict(sorted(dados['pedidos'].items(), key=lambda item: item[0]))
            }
            for cliente_id, dados in sorted(pedidos.items(), key=lambda item: item[0])
        }

        return pedidos_ordenados






    
    def atualizar_status_pedido_entregue(self, id_pedido):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor

        try:
            # Atualiza status e habilitado em um único comando
            mycursor.execute(
                """
                UPDATE tb_pedidos 
                SET status = %s, habilitado = %s 
                WHERE id_pedido = %s
                """, 
                ('entregue', False, id_pedido)
            )
            mydb.commit()  # Confirma as alterações no banco de dados
        except Exception as e:
            print(f"Erro ao atualizar o status do pedido: {e}")  # Log do erro
            mydb.rollback()  # Reverte em caso de erro
        finally:
            mycursor.close()  # Fecha o cursor
            mydb.close()  # Fecha a conexão







    

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
    def inserir_produto(self, nomeP, preco, imagem_blob, descricao, categoria, guarnicoes_novas=[]):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Query SQL para inserir o produto
        sql = "INSERT INTO tb_produto (nome_produto, preco, imagem_blob, descricao, id_categoria) VALUES (%s, %s, %s, %s, %s)"
        valores = (nomeP, preco, imagem_blob, descricao, categoria)
        mycursor.execute(sql, valores)

        # Captura o ID do produto recém-inserido para associar guarnições
        id_produto = mycursor.lastrowid

        # Inserir novas guarnições e associá-las ao produto
        for nova_guarnicao in guarnicoes_novas:
            self.inserir_guarnicao(nova_guarnicao)
            sql_associacao = "INSERT INTO tb_produto_guarnicao (id_produto, id_guarnicao) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_produto, nova_guarnicao))

        mydb.commit()
        mydb.close()
        return True


    
    def inserir_marmita(self, nomeP, preco, imagem, descricao, tamanho, guarnicoes_existentes=[], guarnicoes_novas=[], acompanhamentos_existentes=[], acompanhamentos_novos=[]):
        """
        Insere uma nova marmita no sistema, associando-a à categoria correta. As informações da marmita
        incluem nome, preço, URL da imagem, descrição, tamanho e as guarnições e acompanhamentos associados.
        
        Parâmetros:
        - nomeP: nome da marmita.
        - preco: preço da marmita.
        - imagem: URL da imagem da marmita.
        - descricao: breve descrição da marmita.
        - tamanho: tamanho da marmita (Pequena, Média, Grande).
        - guarnicoes_existentes: lista de IDs das guarnições já existentes.
        - guarnicoes_novas: lista de novas guarnições a serem inseridas.
        - acompanhamentos_existentes: lista de IDs dos acompanhamentos já existentes.
        - acompanhamentos_novos: lista de novos acompanhamentos a serem inseridos.
        
        Retorno:
        - Retorna True se a marmita for inserida com sucesso, ou False em caso de erro.
        """
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        # Inserir marmita na tabela `tb_marmita`
        sql = f"""
        INSERT INTO tb_marmita (nome_marmita, preco, imagem_binaria, descricao, tamanho)
        VALUES (%s, %s, %s, %s, %s)
        """
        mycursor.execute(sql, (nomeP, preco, imagem, descricao, tamanho))
        
        # Capturar o ID da marmita recém-inserida
        id_marmita = mycursor.lastrowid

        # Associar guarnições existentes à marmita
        for id_guarnicao in guarnicoes_existentes:
            sql_associacao = "INSERT INTO tb_marmita_guarnicao (id_marmita, id_guarnicao) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_marmita, id_guarnicao))

        # Inserir e associar novas guarnições
        for nova_guarnicao in guarnicoes_novas:
            _, id_guarnicao = self.inserir_guarnicao(nova_guarnicao)
            sql_associacao = "INSERT INTO tb_marmita_guarnicao (id_marmita, id_guarnicao) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_marmita, id_guarnicao))

        # Associar acompanhamentos existentes à marmita
        for id_acompanhamento in acompanhamentos_existentes:
            sql_associacao = "INSERT INTO tb_marmita_acompanhamento (id_marmita, id_acompanhamento) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_marmita, id_acompanhamento))

        # Inserir e associar novos acompanhamentos
        for novo_acompanhamento in acompanhamentos_novos:
            _, id_acompanhamento = self.inserir_acompanhamento(novo_acompanhamento)
            sql_associacao = "INSERT INTO tb_marmita_acompanhamento (id_marmita, id_acompanhamento) VALUES (%s, %s)"
            mycursor.execute(sql_associacao, (id_marmita, id_acompanhamento))

        mydb.commit()  # Confirma as alterações
        mydb.close()  # Fecha a conexão
        return True






    def exibir_guarnicao(self):
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
    


    def inserir_acompanhamento(self, nome_acompanhamento):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = "INSERT INTO tb_acompanhamentos (nome_acompanhamento) VALUES (%s)"
        mycursor.execute(sql, (nome_acompanhamento,))

        mydb.commit()
        id_acompanhamento = mycursor.lastrowid
        mydb.close()
        return True, id_acompanhamento
    


    def exibir_acompanhamento(self):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()
        sql = "SELECT * FROM tb_acompanhamentos"
        mycursor.execute(sql)
        resultado = mycursor.fetchall()

        lista_acompanhamento = []
        for acompanhamento in resultado:
            lista_acompanhamento.append({
                'nome_acompanhamento': acompanhamento[1],
                'id_acompanhamento': acompanhamento[0]
            })

        mydb.close()
        return lista_acompanhamento if lista_acompanhamento else []







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
    def atualizar_produto(self, id_produto, nome, preco, descricao, url_img=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Base da consulta SQL
        sql = """
            UPDATE tb_produto
            SET nome_produto = %s, preco = %s, descricao = %s
        """
        valores = [nome, preco, descricao]

        # Adicionar a imagem caso fornecida
        if url_img:
            sql += ", url_img = %s"
            valores.append(url_img)

        sql += " WHERE cod_produto = %s"
        valores.append(id_produto)

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
    

    def atualizar_marmita(self, id_marmita, nome, preco, descricao, tamanho, acompanhamentos, guarnicoes, file=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Atualiza os dados da marmita
        sql = """
            UPDATE tb_marmita
            SET nome_marmita = %s, preco = %s, descricao = %s, tamanho = %s
        """
        valores = (nome, preco, descricao, tamanho)

        # Se um arquivo de imagem foi enviado
        if file and file.filename != '':
            diretorio = os.path.join('static', 'uploads')
            filename = f"marmita_{id_marmita}.jpg"
            caminho_imagem = os.path.join(diretorio, filename)
            file.save(caminho_imagem)

            # Atualiza o campo da imagem
            sql += ", url_img = %s"
            valores += (f"/static/uploads/{filename}",)

        sql += " WHERE id_marmita = %s"
        valores += (id_marmita,)

        mycursor.execute(sql, valores)

        # Limpa acompanhamentos e guarnições antigos
        mycursor.execute("DELETE FROM tb_marmita_acompanhamento WHERE id_marmita = %s", (id_marmita,))
        mycursor.execute("DELETE FROM tb_marmita_guarnicao WHERE id_marmita = %s", (id_marmita,))

        # Adiciona novos acompanhamentos e guarnições
        for id_acompanhamento in acompanhamentos:
            mycursor.execute("INSERT INTO tb_marmita_acompanhamento (id_marmita, id_acompanhamento) VALUES (%s, %s)", (id_marmita, id_acompanhamento))
        
        for id_guarnicao in guarnicoes:
            mycursor.execute("INSERT INTO tb_marmita_guarnicao (id_marmita, id_guarnicao) VALUES (%s, %s)", (id_marmita, id_guarnicao))

        mydb.commit()
        mydb.close()








    def obter_imagem_marmita(self, id_marmita):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = "SELECT url_img FROM tb_marmita WHERE id_marmita = %s"
        mycursor.execute(sql, (id_marmita,))
        resultado = mycursor.fetchone()

        mydb.close()

        if resultado:
            return resultado[0]  # Retorna o caminho da imagem
        return None  # Retorna None se não encontrar
