from conexao import Conexao
from hashlib import sha256
import base64

class Sistema:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None




    import base64

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
            imagem_blob = produto[7]  # Blob da imagem (posição 7)
            imagem_url = produto[3]   # URL da imagem (posição 3)

            if imagem_blob:  # Caso o blob esteja presente
                # Converte o blob para uma string Base64
                imagem_base64 = base64.b64encode(imagem_blob).decode('utf-8')
                # Cria o URL de dados para a imagem
                imagem_produto = f"data:image/jpeg;base64,{imagem_base64}"
            elif imagem_url:  # Caso o blob não exista, mas o URL esteja presente
                imagem_produto = imagem_url  # Usa o URL diretamente
            else:  # Caso não exista nem blob nem URL
                imagem_produto = None

            lista_produtos.append({
                'nome_produto': produto[1],
                'preco': produto[2],
                'imagem_produto': imagem_produto,  # Base64 ou URL
                'categoria': produto[5],
                'descricao': produto[4],
                'id_produto': produto[0],
                'habilitado': produto[6]
            })

        mydb.close()  # Fecha a conexão com o banco de dados
        return lista_produtos if lista_produtos else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado



    def exibir_produtos(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL com JOIN para obter o nome e o ID da categoria
        sql = """
        SELECT p.cod_produto, p.nome_produto, p.preco, p.url_img, p.descricao, c.id_categoria, c.nome, p.imagem_blob
        FROM tb_produto p
        JOIN tb_categoria c ON p.id_categoria = c.id_categoria
        WHERE p.habilitado = 1
        """
        mycursor.execute(sql)      # Executa a consulta
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        produtos_por_categoria = {}

        # Itera sobre os resultados e agrupa os produtos por categoria
        for produto in resultado:
            categoria_id = produto[5]
            categoria_nome = produto[6]
            url_img = produto[3]  # URL da imagem
            blob_imagem = produto[7]  # Blob da imagem

            # Lógica para determinar a imagem do produto
            if url_img:  # Se a URL estiver disponível
                imagem_produto = url_img
            elif blob_imagem:  # Se o blob estiver disponível
                imagem_base64 = base64.b64encode(blob_imagem).decode('utf-8')
                imagem_produto = f"data:image/jpeg;base64,{imagem_base64}"
            else:  # Se nenhuma imagem estiver disponível
                imagem_produto = None

            # Agrupa os produtos por categoria
            if categoria_id not in produtos_por_categoria:
                produtos_por_categoria[categoria_id] = {
                    'nome_categoria': categoria_nome,  # Armazena o nome da categoria
                    'produtos': []
                }

            produtos_por_categoria[categoria_id]['produtos'].append({
                'id_produto': produto[0],
                'nome_produto': produto[1],
                'preco': produto[2],
                'imagem_produto': imagem_produto,  # URL ou Base64
                'descricao': produto[4]
            })

        mydb.close()  # Fecha a conexão com o banco de dados
        return produtos_por_categoria if produtos_por_categoria else {}  # Retorna os produtos agrupados ou um dicionário vazio





    # Método para exibir um único produto com base no ID
    def exibir_produto(self, id):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para selecionar um produto específico pelo ID
        sql = "SELECT * FROM tb_produto WHERE cod_produto = %s"
        mycursor.execute(sql, (id,))
        resultado = mycursor.fetchone()  # Obtém o resultado único

        if not resultado:
            return None  # Retorna None caso o produto não seja encontrado

        # Recupera as informações do produto
        imagem_url = resultado[3]  # URL da imagem (posição 3)
        imagem_blob = resultado[7]  # Blob da imagem (posição 7)

        # Lógica para definir a imagem do produto
        if imagem_url:  # Se o URL da imagem estiver disponível
            imagem_produto = imagem_url
        elif imagem_blob:  # Se o blob estiver disponível
            imagem_base64 = base64.b64encode(imagem_blob).decode('utf-8')
            imagem_produto = f"data:image/jpeg;base64,{imagem_base64}"
        else:  # Se nenhum estiver disponível
            imagem_produto = None

        # Cria um dicionário para o produto
        dicionario_produto = {
            'nome_produto': resultado[1],
            'preco': resultado[2],
            'imagem_produto': imagem_produto,  # Base64 ou URL
            'descricao': resultado[4],
            'cod_produto': resultado[0]
        }

        mydb.commit()
        mydb.close()
        return [dicionario_produto]  # Retorna a lista com um único produto
    


    def exibir_marmita(self, id_marmita):
        # Conexão e consulta ao banco
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para selecionar a marmita, guarnições e acompanhamentos associados
        sql_marmita = """
        SELECT 
            m.id_marmita, m.nome_marmita, m.preco, m.tamanho, m.descricao, m.url_img,
            GROUP_CONCAT(DISTINCT CONCAT(g.id_guarnicao, ':', g.nome_guarnicao) SEPARATOR ', ') AS guarnicoes,
            GROUP_CONCAT(DISTINCT CONCAT(a.id_acompanhamento, ':', a.nome_acompanhamento) SEPARATOR ', ') AS acompanhamentos,
             m.imagem_binaria
        FROM 
            tb_marmita AS m
        LEFT JOIN tb_marmita_guarnicao AS mg ON m.id_marmita = mg.id_marmita
        LEFT JOIN tb_guarnicao AS g ON mg.id_guarnicao = g.id_guarnicao
        LEFT JOIN tb_marmita_acompanhamento AS ma ON m.id_marmita = ma.id_marmita
        LEFT JOIN tb_acompanhamentos AS a ON ma.id_acompanhamento = a.id_acompanhamento
        WHERE m.id_marmita = %s
        GROUP BY m.id_marmita;
        """
        mycursor.execute(sql_marmita, (id_marmita,))
        resultado = mycursor.fetchone()

        # Caso a consulta não encontre resultados
        if not resultado:
            return None

        # Função auxiliar para dividir os resultados de guarnições e acompanhamentos
        def processar_itens(itens):
            if not itens:
                return []
            lista_itens = []
            for item in itens.split(', '):
                id_item, nome_item = item.split(':')
                lista_itens.append({'id': id_item, 'nome': nome_item})
            return lista_itens

        # Processa guarnições e acompanhamentos associados à marmita
        guarnicoes_associadas = processar_itens(resultado[6])  # IDs e nomes das guarnições
        acompanhamentos_associados = processar_itens(resultado[7])  # IDs e nomes dos acompanhamentos

        # Consulta SQL para pegar todas as guarnições
        sql_todas_guarnicoes = "SELECT id_guarnicao, nome_guarnicao FROM tb_guarnicao"
        mycursor.execute(sql_todas_guarnicoes)
        todas_guarnicoes = [{'id': str(row[0]), 'nome': row[1]} for row in mycursor.fetchall()]

        # Consulta SQL para pegar todos os acompanhamentos
        sql_todos_acompanhamentos = "SELECT id_acompanhamento, nome_acompanhamento FROM tb_acompanhamentos"
        mycursor.execute(sql_todos_acompanhamentos)
        todos_acompanhamentos = [{'id': str(row[0]), 'nome': row[1]} for row in mycursor.fetchall()]

        # Função para converter imagem binária em base64
        def converter_imagem_binaria(img_binaria):
            imagem_base64 = base64.b64encode(img_binaria).decode('utf-8')
            imagem_marmita = f"data:image/jpeg;base64,{imagem_base64}"
            return imagem_marmita
        # Define a imagem da marmita (binária ou URL)
        imagem_marmita = None

        if resultado[8]:  # Verifica se há conteúdo binário
            try:
                # Tenta converter a imagem binária para base64
                imagem_marmita = converter_imagem_binaria(resultado[8])
            except Exception as e:
                print(f"Erro ao converter imagem binária: {e}")
                imagem_marmita = resultado[5]  # Fallback para a URL da imagem
        else:
            imagem_marmita = resultado[5]  # Se não houver binário, utiliza a URL


        # Organiza os dados da marmita
        dados_marmita = {
            'id_marmita': resultado[0],  # ID da marmita
            'nome_marmita': resultado[1],  # Nome da marmita
            'preco': resultado[2],  # Preço
            'tamanho': resultado[3],  # Tamanho
            'descricao': resultado[4],  # Descrição
            'imagem_marmita': imagem_marmita,  # Imagem (binária ou URL)
            'guarnicoes': guarnicoes_associadas,  # Guarnições associadas à marmita
            'acompanhamentos': acompanhamentos_associados,  # Acompanhamentos associados à marmita
            'todas_guarnicoes': todas_guarnicoes,  # Todas as guarnições disponíveis
            'todos_acompanhamentos': todos_acompanhamentos  # Todos os acompanhamentos disponíveis
        }

        # Fecha a conexão
        mydb.close()

        # Retorna a lista com o dicionário da marmita
        return [dados_marmita]












    def exibir_marmitas(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar marmitas habilitadas
        sql = """
        SELECT m.id_marmita, m.nome_marmita, m.preco, m.tamanho, m.descricao, 
            m.url_img, m.imagem_binaria, m.habilitado
        FROM tb_marmita m
        WHERE m.habilitado = 1
        """
        mycursor.execute(sql)  # Executa a consulta
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        marmitas_por_tamanho = {}

        # Itera sobre os resultados e agrupa as marmitas por tamanho
        for marmita in resultado:
            tamanho = marmita[3]  # Obtém o tamanho da marmita (Pequena, Média, Grande)
            url_img = marmita[5]  # URL da imagem
            blob_imagem = marmita[6]  # Blob da imagem

            # Lógica para determinar a imagem da marmita
            if url_img:  # Se a URL estiver disponível
                imagem_marmita = url_img
            elif blob_imagem:  # Se o blob estiver disponível
                imagem_base64 = base64.b64encode(blob_imagem).decode('utf-8')
                imagem_marmita = f"data:image/jpeg;base64,{imagem_base64}"
            else:  # Se nenhuma imagem estiver disponível
                imagem_marmita = None

            # Agrupa as marmitas por tamanho
            if tamanho not in marmitas_por_tamanho:
                marmitas_por_tamanho[tamanho] = {
                    'tamanho': tamanho,  # Armazena o tamanho da marmita
                    'marmitas': []
                }

            marmitas_por_tamanho[tamanho]['marmitas'].append({
                'id_marmita': marmita[0],
                'nome_marmita': marmita[1],
                'preco': marmita[2],
                'imagem_marmita': imagem_marmita,  # URL ou Base64
                'descricao': marmita[4]
            })

        mydb.close()  # Fecha a conexão com o banco de dados
        return marmitas_por_tamanho if marmitas_por_tamanho else {}  # Retorna as marmitas agrupadas ou um dicionário vazio



    
    def exibir_marmitas_adm(self):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()   # Cria um cursor para executar queries

        # Consulta SQL para selecionar todos os produtos
        sql = "SELECT id_marmita, nome_marmita, preco, tamanho, descricao, url_img, imagem_binaria, habilitado FROM tb_marmita"
        mycursor.execute(sql)      # Executa a consulta
        resultado = mycursor.fetchall()  # Obtém todos os resultados

        lista_marmitas = []

        # Itera sobre os resultados e adiciona cada marmita à lista
        for produto in resultado:
            id_marmita = produto[0]
            nome_marmita = produto[1]
            preco = produto[2]
            tamanho = produto[3]
            descricao = produto[4]
            url_img = produto[5]  # URL da imagem
            blob_imagem = produto[6]  # Imagem em formato binário
            habilitado = produto[7]  # Estado habilitado ou não

            # Lógica para determinar a imagem da marmita
            if url_img:  # Se a URL estiver disponível
                imagem_marmita = url_img
            elif blob_imagem:  # Se o blob estiver disponível
                # Converte a imagem binária para Base64
                imagem_base64 = base64.b64encode(blob_imagem).decode('utf-8')
                imagem_marmita = f"data:image/jpeg;base64,{imagem_base64}"
            else:  # Se nenhuma imagem estiver disponível
                imagem_marmita = None

            # Adiciona os dados da marmita à lista
            lista_marmitas.append({
                'id_marmita': id_marmita,
                'nome_marmita': nome_marmita,
                'preco': preco,
                'tamanho': tamanho,
                'descricao': descricao,
                'imagem_marmita': imagem_marmita,
                'habilitado': habilitado
            })

        mydb.close()  # Fecha a conexão com o banco de dados

        return lista_marmitas if lista_marmitas else []  # Retorna a lista de produtos ou uma lista vazia se nenhum produto for encontrado



   


    # Método para exibir todos os pedidos de um cliente específico com detalhes dos produtos e marmitas
    def exibir_historico(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = """
            SELECT p.id_pedido, cl.id_cliente, cl.nome_comp, cl.telefone, 
                pr.nome_produto, pr.preco AS preco_produto, pp.quantidade, 
                m.nome_marmita, m.preco AS preco_marmita, 
                p.data_pedido, p.status, p.hora_pedido
            FROM tb_pedidos p
            JOIN tb_cliente cl ON p.id_cliente = cl.id_cliente
            JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE cl.id_cliente = %s
            ORDER BY p.data_pedido DESC
        """
        mycursor.execute(sql, (id_cliente,))
        resultados = mycursor.fetchall()

        pedidos = {}

        for resultado in resultados:
            id_pedido = resultado[0]
            nome_cliente = resultado[2]
            telefone_cliente = resultado[3]
            nome_produto = resultado[4]
            preco_produto = resultado[5]
            quantidade_produto = resultado[6]
            nome_marmita = resultado[7]
            preco_marmita = resultado[8]
            data_pedido = resultado[9].strftime('%d/%m/%Y') if resultado[11] else None
            status_pedido = resultado[10]
            hora_pedido = str(resultado[11]) if resultado[11] else None  # Converte hora_pedido para string

            if id_cliente not in pedidos:
                pedidos[id_cliente] = {
                    'nome_cliente': nome_cliente,
                    'telefone': telefone_cliente,
                    'pedidos': {}
                }

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

            if nome_produto:
                total_produto = preco_produto * quantidade_produto
                pedidos[id_cliente]['pedidos'][id_pedido]['produtos'].append({
                    'nome_produto': nome_produto,
                    'preco': preco_produto,
                    'quantidade': quantidade_produto
                })
                pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += total_produto

            if nome_marmita:
                pedidos[id_cliente]['pedidos'][id_pedido]['marmitas'].append({
                    'nome_marmita': nome_marmita,
                    'preco': preco_marmita,
                    'quantidade': quantidade_produto
                })
                pedidos[id_cliente]['pedidos'][id_pedido]['total_preco'] += preco_marmita * quantidade_produto

        for id_pedido in pedidos[id_cliente]['pedidos']:
            sql_guarnicoes = """
                SELECT g.nome_guarnicao 
                FROM tb_guarnicoes_pedidos AS cg
                JOIN tb_guarnicao AS g ON cg.guarnicao = g.id_guarnicao
                WHERE cg.id_pedido = %s
            """
            mycursor.execute(sql_guarnicoes, (id_pedido,))
            guarnicoes = [row[0] for row in mycursor.fetchall()]
            pedidos[id_cliente]['pedidos'][id_pedido]['guarnicoes'] = guarnicoes

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
        return pedidos






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



    def cancelar_pedido(self, id_pedido, motivo_cancelamento):
        mydb = Conexao.conectar()  # Conecta ao banco de dados
        mycursor = mydb.cursor()

        try:
            # Atualiza o status do pedido e define habilitado como 0
            sql = "UPDATE tb_pedidos SET status = 'Cancelado', habilitado = 0, motivo_cancelamento = %s WHERE id_pedido = %s"
            mycursor.execute(sql, (motivo_cancelamento, id_pedido))

            mydb.commit()  # Confirma a alteração
            return {"message": "Pedido cancelado com sucesso!"}  # Retorna mensagem de sucesso
        except Exception as e:
            mydb.rollback()  # Reverte a transação em caso de erro
            return {"error": f"Erro ao cancelar o pedido: {str(e)}"}
        finally:
            mydb.close()  # Fecha a conexão com o banco de dados



    def obter_dados_cliente_por_pedido(self, id_pedido):
        """
        Obtém os dados do cliente associados a um pedido específico.
        
        :param id_pedido: ID do pedido para o qual os dados do cliente serão buscados.
        :return: Um dicionário com o telefone e nome do cliente, ou None se não for encontrado.
        """
        try:
            # Query para buscar os dados do cliente associados ao pedido
            query = """
            SELECT c.telefone, c.nome_comp
            FROM tb_cliente c
            JOIN tb_pedidos p ON c.id_cliente = p.id_cliente
            WHERE p.id_pedido = %s
            """
            # Executa a query passando o ID do pedido como parâmetro
            dados = self.executar_query(query, (id_pedido,), fetch=True)
            
            # Verifica se algum dado foi retornado
            if dados:
                # Retorna o primeiro resultado encontrado
                return {'telefone': dados[0]['telefone'], 'nome': dados[0]['nome_comp']}
            
            # Caso nenhum dado seja encontrado, retorna None
            return None
        
        except Exception as e:
            # Loga o erro para depuração
            print(f"Erro ao obter dados do cliente: {e}")
            return None


    def executar_query(self, query, params=None, fetch=False):
        """
        Executa uma query no banco de dados.
        
        :param query: A string SQL a ser executada.
        :param params: Uma tupla com os parâmetros para a query.
        :param fetch: Define se a função deve retornar os resultados (True) ou não (False).
        :return: Os resultados da query se fetch=True, ou None caso contrário.
        """
        try:
            # Conecta ao banco de dados
            conn = Conexao.conectar()  # Certifique-se de que esse método está implementado
            cursor = conn.cursor(dictionary=True)  # Retorna resultados como dicionários
            
            # Executa a query com os parâmetros
            cursor.execute(query, params)
            
            # Se fetch=True, retorna os resultados da query
            if fetch:
                result = cursor.fetchall()
                return result
            
            # Confirma alterações no banco (para operações como INSERT/UPDATE/DELETE)
            conn.commit()
        
        except mysql.connector.Error as e:
            # Loga o erro específico do banco
            print(f"Erro ao executar a query: {e}")
            return None
        
        except Exception as e:
            # Loga outros erros genéricos
            print(f"Erro inesperado ao executar a query: {e}")
            return None
        
        finally:
            # Fecha o cursor e a conexão
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
