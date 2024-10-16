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

        # Verifica se o item (produto ou marmita) já está no carrinho do cliente
        sql_verificar = """
            SELECT quantidade FROM tb_carrinho
            WHERE id_cliente = %s AND (cod_produto = %s OR id_marmita = %s)
        """
        mycursor.execute(sql_verificar, (id_cliente, cod_produto, id_marmita))
        resultado = mycursor.fetchone()

        if resultado:
            # Se o item já estiver no carrinho, atualiza a quantidade
            nova_quantidade = resultado[0] + 1
            sql_update = """
                UPDATE tb_carrinho
                SET quantidade = %s
                WHERE id_cliente = %s AND (cod_produto = %s OR id_marmita = %s)
            """
            mycursor.execute(sql_update, (nova_quantidade, id_cliente, cod_produto, id_marmita))
        else:
            # Se o item não estiver no carrinho, insere um novo item
            sql_inserir = """
                INSERT INTO tb_carrinho (id_cliente, cod_produto, id_marmita, quantidade)
                VALUES (%s, %s, %s, 1)
            """
            mycursor.execute(sql_inserir, (id_cliente, cod_produto, id_marmita))

            # Obtém o ID do carrinho recém-inserido
            id_carrinho = mycursor.lastrowid

            # Inserindo guarnições na tabela tb_carrinho_guarnicao
            if guarnicoes_selecionadas:
                sql_inserir_guarnicao = """
                    INSERT INTO tb_carrinho_guarnicao (id_carrinho, guarnicao)
                    VALUES (%s, %s)
                """
                for guarnicao in guarnicoes_selecionadas:  # Itera diretamente sobre a lista
                    if guarnicao:  # Evita inserir valores vazios
                        mycursor.execute(sql_inserir_guarnicao, (id_carrinho, guarnicao))

            # Inserindo acompanhamentos na tabela tb_carrinho_acompanhamento
            if acompanhamentos_selecionados:
                sql_inserir_acompanhamento = """
                    INSERT INTO tb_carrinho_acompanhamento (id_carrinho, acompanhamento)
                    VALUES (%s, %s)
                """
                for acompanhamento in acompanhamentos_selecionados:  # Itera diretamente sobre a lista
                    if acompanhamento:  # Evita inserir valores vazios
                        mycursor.execute(sql_inserir_acompanhamento, (id_carrinho, acompanhamento))

        mydb.commit()
        mydb.close()
        return True






    # Método para exibir os produtos e marmitas no carrinho de um cliente
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

        # Itera sobre os resultados de marmitas e adiciona ao carrinho
        for resultado in resultado_marmitas:
            preco_marmita = resultado[2]
            quantidade_marmita = resultado[5]

            lista_carrinho['marmitas'].append({
                'nome_marmita': resultado[1],
                'preco': preco_marmita,
                'imagem_produto': resultado[3],  # Agora pegando a imagem da tabela tb_marmitas
                'id_carrinho': resultado[4],
                'quantidade': quantidade_marmita
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
            # Remove guarnições relacionadas
            sql_remover_guarnicoes = "DELETE FROM tb_carrinho_guarnicao WHERE id_carrinho = (SELECT id_carrinho FROM tb_carrinho WHERE id_cliente = %s)"
            mycursor.execute(sql_remover_guarnicoes, (id_cliente,))

            # Remove acompanhamentos relacionados
            sql_remover_acompanhamentos = "DELETE FROM tb_carrinho_acompanhamento WHERE id_carrinho = (SELECT id_carrinho FROM tb_carrinho WHERE id_cliente = %s)"
            mycursor.execute(sql_remover_acompanhamentos, (id_cliente,))

            # Agora remove o produto do carrinho
            sql_remover_carrinho = "DELETE FROM tb_carrinho WHERE id_cliente = %s"
            mycursor.execute(sql_remover_carrinho, (id_cliente,))

            mydb.commit()
            print(f"Todos os produtos do cliente {id_cliente} foram removidos do carrinho com sucesso.")
        except Exception as e:
            mydb.rollback()
            print(f"Erro ao remover os produtos do carrinho: {e}")
        finally:
            mydb.close()
