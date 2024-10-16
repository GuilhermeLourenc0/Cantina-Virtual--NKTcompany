from conexao import Conexao
from hashlib import sha256

class Carrinho:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None


    def inserir_item_carrinho(self, cod_produto, id_marmita, id_cliente, guarnicoes_selecionadas=None, acompanhamentos_selecionados=None):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            if id_marmita:
                # Verifica se já existe uma marmita com as mesmas guarnições e acompanhamentos no carrinho
                sql_verificar_marmita = """
                    SELECT c.id_carrinho
                    FROM tb_carrinho c
                    LEFT JOIN tb_carrinho_guarnicao cg ON c.id_carrinho = cg.id_carrinho
                    LEFT JOIN tb_carrinho_acompanhamento ca ON c.id_carrinho = ca.id_carrinho
                    WHERE c.id_cliente = %s AND c.id_marmita = %s
                    GROUP BY c.id_carrinho
                    HAVING 
                        (COALESCE(GROUP_CONCAT(DISTINCT cg.guarnicao ORDER BY cg.guarnicao), '') = %s) AND 
                        (COALESCE(GROUP_CONCAT(DISTINCT ca.acompanhamento ORDER BY ca.acompanhamento), '') = %s)
                """
                
                # Concatena as guarnições e acompanhamentos selecionados para comparação
                guarnicoes_str = ','.join(sorted(guarnicoes_selecionadas)) if guarnicoes_selecionadas else ''
                acompanhamentos_str = ','.join(sorted(acompanhamentos_selecionados)) if acompanhamentos_selecionados else ''

                # Executa a consulta para verificar se existe uma marmita igual no carrinho
                mycursor.execute(sql_verificar_marmita, (
                    id_cliente, id_marmita, guarnicoes_str, acompanhamentos_str
                ))
                resultado = mycursor.fetchone()

                if resultado:
                    # Marmita com as mesmas guarnições e acompanhamentos já existe, atualiza a quantidade
                    id_carrinho = resultado[0]
                    sql_atualizar_quantidade = """
                        UPDATE tb_carrinho
                        SET quantidade = quantidade + 1
                        WHERE id_carrinho = %s
                    """
                    mycursor.execute(sql_atualizar_quantidade, (id_carrinho,))
                else:
                    # Se não existir marmita com as mesmas características, insere uma nova
                    sql_inserir_carrinho = """
                        INSERT INTO tb_carrinho (id_cliente, cod_produto, id_marmita, quantidade)
                        VALUES (%s, %s, %s, 1)
                    """
                    mycursor.execute(sql_inserir_carrinho, (id_cliente, cod_produto, id_marmita))

                    # Obtém o ID do carrinho recém-inserido
                    id_carrinho = mycursor.lastrowid

                    # Inserir guarnições na tabela tb_carrinho_guarnicao
                    if guarnicoes_selecionadas:
                        sql_inserir_guarnicao = """
                            INSERT INTO tb_carrinho_guarnicao (id_carrinho, guarnicao)
                            VALUES (%s, %s)
                        """
                        for guarnicao in guarnicoes_selecionadas:
                            mycursor.execute(sql_inserir_guarnicao, (id_carrinho, guarnicao))

                    # Inserir acompanhamentos na tabela tb_carrinho_acompanhamento
                    if acompanhamentos_selecionados:
                        sql_inserir_acompanhamento = """
                            INSERT INTO tb_carrinho_acompanhamento (id_carrinho, acompanhamento)
                            VALUES (%s, %s)
                        """
                        for acompanhamento in acompanhamentos_selecionados:
                            mycursor.execute(sql_inserir_acompanhamento, (id_carrinho, acompanhamento))

            else:
                # Para produtos, verifica se já existe no carrinho e atualiza a quantidade
                sql_verificar_produto = """
                    SELECT quantidade FROM tb_carrinho
                    WHERE id_cliente = %s AND cod_produto = %s
                """
                mycursor.execute(sql_verificar_produto, (id_cliente, cod_produto))
                resultado = mycursor.fetchone()

                if resultado:
                    nova_quantidade = resultado[0] + 1
                    sql_update_produto = """
                        UPDATE tb_carrinho
                        SET quantidade = %s
                        WHERE id_cliente = %s AND cod_produto = %s
                    """
                    mycursor.execute(sql_update_produto, (nova_quantidade, id_cliente, cod_produto))
                else:
                    # Se o produto não existir no carrinho, insere um novo
                    sql_inserir_produto = """
                        INSERT INTO tb_carrinho (id_cliente, cod_produto, quantidade)
                        VALUES (%s, %s, 1)
                    """
                    mycursor.execute(sql_inserir_produto, (id_cliente, cod_produto))

            mydb.commit()

        except Exception as e:
            mydb.rollback()
            print(f"Erro ao inserir item no carrinho: {e}")
        finally:
            mydb.close()










    def exibir_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        # Consulta SQL para obter produtos no carrinho
        sql_produtos = """
            SELECT p.cod_produto, p.nome_produto, p.preco, p.url_img, c.id_carrinho, c.quantidade
            FROM tb_carrinho AS c
            JOIN tb_produto AS p ON c.cod_produto = p.cod_produto
            WHERE c.id_cliente = %s;
        """
        mycursor.execute(sql_produtos, (id_cliente,))
        resultado_produtos = mycursor.fetchall()

        # Consulta SQL para obter marmitas no carrinho
        sql_marmitas = """
            SELECT m.id_marmita, m.nome_marmita, m.preco, m.url_img, c.id_carrinho, c.quantidade
            FROM tb_carrinho AS c
            JOIN tb_marmita AS m ON c.id_marmita = m.id_marmita
            WHERE c.id_cliente = %s;
        """
        mycursor.execute(sql_marmitas, (id_cliente,))
        resultado_marmitas = mycursor.fetchall()

        lista_carrinho = {
            'produtos': [],
            'marmitas': []
        }
        total_preco = 0  # Inicializa o total de preço

        # Itera sobre os resultados de produtos e adiciona ao carrinho
        for resultado in resultado_produtos:
            preco_produto = resultado[2]
            quantidade_produto = resultado[5]

            lista_carrinho['produtos'].append({
                'nome_produto': resultado[1],
                'preco': preco_produto,
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[4],
                'quantidade': quantidade_produto
            })

            total_preco += preco_produto * quantidade_produto  # Atualiza o total de preço

        # Itera sobre os resultados de marmitas e adiciona ao carrinho, buscando guarnições e acompanhamentos
        for resultado in resultado_marmitas:
            preco_marmita = resultado[2]
            quantidade_marmita = resultado[5]

            # Consulta para obter guarnições da marmita no carrinho
            sql_guarnicoes = """
                SELECT g.nome_guarnicao 
                FROM tb_carrinho_guarnicao AS cg
                JOIN tb_guarnicao AS g ON cg.guarnicao = g.id_guarnicao
                WHERE cg.id_carrinho = %s
            """
            mycursor.execute(sql_guarnicoes, (resultado[4],))
            guarnicoes = [row[0] for row in mycursor.fetchall()]

            # Consulta para obter acompanhamentos da marmita no carrinho
            sql_acompanhamentos = """
                SELECT a.nome_acompanhamento 
                FROM tb_carrinho_acompanhamento AS ca
                JOIN tb_acompanhamentos AS a ON ca.acompanhamento = a.id_acompanhamento
                WHERE ca.id_carrinho = %s
            """
            mycursor.execute(sql_acompanhamentos, (resultado[4],))
            acompanhamentos = [row[0] for row in mycursor.fetchall()]

            # Adiciona as guarnições e acompanhamentos ao dicionário da marmita
            lista_carrinho['marmitas'].append({
                'nome_marmita': resultado[1],
                'preco': preco_marmita,
                'imagem_produto': resultado[3],
                'id_carrinho': resultado[4],
                'quantidade': quantidade_marmita,
                'guarnicoes': guarnicoes,
                'acompanhamentos': acompanhamentos
            })

            total_preco += preco_marmita * quantidade_marmita  # Atualiza o total de preço

        mydb.close()
        total_preco_formatado = "{:.2f}".format(total_preco)  # Formata o total de preço
        return {
            'produtos': lista_carrinho['produtos'],
            'marmitas': lista_carrinho['marmitas'],
            'total_preco': total_preco_formatado
        }










    # Método para excluir um produto do carrinho
    def remover_produto_carrinho(self, id_carrinho):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            # Remove guarnições relacionadas
            sql_remover_guarnicoes = "DELETE FROM tb_carrinho_guarnicao WHERE id_carrinho = %s"
            mycursor.execute(sql_remover_guarnicoes, (id_carrinho,))

            # Remove acompanhamentos relacionados
            sql_remover_acompanhamentos = "DELETE FROM tb_carrinho_acompanhamento WHERE id_carrinho = %s"
            mycursor.execute(sql_remover_acompanhamentos, (id_carrinho,))

            # Agora remove o produto do carrinho
            sql_remover_carrinho = "DELETE FROM tb_carrinho WHERE id_carrinho = %s"
            mycursor.execute(sql_remover_carrinho, (id_carrinho,))

            mydb.commit()
            print(f"Produto com ID {id_carrinho} removido com sucesso do carrinho.")
        except Exception as e:
            mydb.rollback()
            print(f"Erro ao remover o produto do carrinho: {e}")
        finally:
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

    def enviar_carrinho(self, id_cliente, itens):
        try:
            # Conexão ao banco de dados
            mydb = Conexao.conectar()
            mycursor = mydb.cursor()

            # 1. Verifica se o carrinho tem itens
            sql_carrinho = "SELECT cod_produto, id_marmita, quantidade FROM tb_carrinho WHERE id_cliente = %s"
            mycursor.execute(sql_carrinho, (id_cliente,))
            itens_carrinho = mycursor.fetchall()

            if not itens_carrinho:
                print("Carrinho está vazio, não é possível enviar o pedido.")
                return False  # Retorna falso se o carrinho estiver vazio

            # 2. Insere um novo pedido na tabela `tb_pedidos`
            sql_pedido = "INSERT INTO tb_pedidos (id_cliente, data_pedido, status) VALUES (%s, CURDATE(), 'Pendente')"
            mycursor.execute(sql_pedido, (id_cliente,))
            id_pedido = mycursor.lastrowid  # Obtém o ID do novo pedido

            # 3. Insere os produtos e marmitas do carrinho na tabela `tb_produtos_pedidos`
            for item in itens_carrinho:
                cod_produto = item[0]
                id_marmita = item[1]
                quantidade = item[2]

                if cod_produto:  # Se for um produto
                    sql_produtos_pedido = "INSERT INTO tb_produtos_pedidos (id_pedido, cod_produto, quantidade) VALUES (%s, %s, %s)"
                    mycursor.execute(sql_produtos_pedido, (id_pedido, cod_produto, quantidade))
                elif id_marmita:  # Se for uma marmita
                    sql_marmitas_pedido = "INSERT INTO tb_produtos_pedidos (id_pedido, id_marmita, quantidade) VALUES (%s, %s, %s)"
                    mycursor.execute(sql_marmitas_pedido, (id_pedido, id_marmita, quantidade))

                    # 4. Insere guarnições e acompanhamentos da marmita
                    sql_guarnicoes = "SELECT guarnicao FROM tb_carrinho_guarnicao WHERE id_carrinho = (SELECT id_carrinho FROM tb_carrinho WHERE id_cliente = %s AND id_marmita = %s)"
                    mycursor.execute(sql_guarnicoes, (id_cliente, id_marmita))
                    guarnicoes = mycursor.fetchall()
                    for guarnicao in guarnicoes:
                        sql_inserir_guarnicao = "INSERT INTO tb_guarnicoes_pedidos (id_pedido, guarnicao) VALUES (%s, %s)"
                        mycursor.execute(sql_inserir_guarnicao, (id_pedido, guarnicao[0]))

                    sql_acompanhamentos = "SELECT acompanhamento FROM tb_carrinho_acompanhamento WHERE id_carrinho = (SELECT id_carrinho FROM tb_carrinho WHERE id_cliente = %s AND id_marmita = %s)"
                    mycursor.execute(sql_acompanhamentos, (id_cliente, id_marmita))
                    acompanhamentos = mycursor.fetchall()
                    for acompanhamento in acompanhamentos:
                        sql_inserir_acompanhamento = "INSERT INTO tb_acompanhamentos_pedidos (id_pedido, acompanhamento) VALUES (%s, %s)"
                        mycursor.execute(sql_inserir_acompanhamento, (id_pedido, acompanhamento[0]))

            # 5. Remove os itens do carrinho após finalizar o pedido
            self.remover_produto_carrinho(id_cliente)

            # Confirma as operações
            mydb.commit()
            print(f"Pedido {id_pedido} enviado com sucesso para o cliente {id_cliente}.")
            return True

        except Exception as e:
            # Se ocorrer algum erro, desfaz todas as alterações
            mydb.rollback()
            print(f"Erro ao enviar o pedido: {e}")
            return False

        finally:
            # Fecha a conexão com o banco de dados
            mydb.close()


    def remover_todo_carrinho(self, id_cliente):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        try:
            # Obter todos os ids do carrinho relacionados ao cliente
            sql_obter_ids_carrinho = "SELECT id_carrinho FROM tb_carrinho WHERE id_cliente = %s"
            mycursor.execute(sql_obter_ids_carrinho, (id_cliente,))
            ids_carrinho = mycursor.fetchall()

            if not ids_carrinho:
                print(f"Carrinho do cliente {id_cliente} está vazio.")
                return

            ids_carrinho_list = [str(id[0]) for id in ids_carrinho]  # Converte os ids para uma lista

            # Remove guarnições relacionadas ao carrinho
            sql_remover_guarnicoes = f"DELETE FROM tb_carrinho_guarnicao WHERE id_carrinho IN ({','.join(ids_carrinho_list)})"
            mycursor.execute(sql_remover_guarnicoes)

            # Remove acompanhamentos relacionados ao carrinho
            sql_remover_acompanhamentos = f"DELETE FROM tb_carrinho_acompanhamento WHERE id_carrinho IN ({','.join(ids_carrinho_list)})"
            mycursor.execute(sql_remover_acompanhamentos)

            # Remove todos os itens do carrinho
            sql_remover_carrinho = f"DELETE FROM tb_carrinho WHERE id_cliente = %s"
            mycursor.execute(sql_remover_carrinho, (id_cliente,))

            # Confirma a remoção
            mydb.commit()
            print(f"Todos os itens do cliente {id_cliente} foram removidos do carrinho com sucesso.")

        except Exception as e:
            # Em caso de erro, desfaz as alterações
            mydb.rollback()
            print(f"Erro ao remover os produtos do carrinho: {e}")

        finally:
            # Fecha a conexão com o banco de dados
            mydb.close()

