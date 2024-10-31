from conexao import Conexao
from datetime import datetime


class Relatorio:
    def __init__(self):
        # Inicializa a classe Sistema sem variáveis de instância necessárias.
        self.tel = None
        self.id_produto = None



    def exibir_relatorio_entregue(self, data_inicial, data_final):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = """
            SELECT
                p.id_pedido,
                p.data_pedido,
                p.hora_pedido,
                p.status,
                SUM(pp.quantidade * CASE
                    WHEN pp.cod_produto IS NOT NULL THEN pr.preco
                    WHEN pp.id_marmita IS NOT NULL THEN m.preco
                    ELSE 0
                END) AS valor_total
            FROM tb_pedidos p
            LEFT JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE p.data_pedido BETWEEN %s AND %s AND p.status = 'entregue'
            GROUP BY p.id_pedido
        """

        # Subconsultas para valores gerais e quantidade
        sql_total = """
            SELECT
                SUM(pp.quantidade * CASE
                    WHEN pp.cod_produto IS NOT NULL THEN pr.preco
                    WHEN pp.id_marmita IS NOT NULL THEN m.preco
                    ELSE 0
                END) AS valor_total_geral,
                COUNT(p.id_pedido) AS total_pedidos
            FROM tb_pedidos p
            LEFT JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE p.data_pedido BETWEEN %s AND %s AND p.status = 'entregue'
        """

        # Executa a consulta principal para os pedidos
        mycursor.execute(sql, (data_inicial, data_final))
        pedidos_resultados = mycursor.fetchall()

        # Executa a subconsulta para valores gerais
        mycursor.execute(sql_total, (data_inicial, data_final))
        total_resultado = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        # Formatação dos dados para o template
        pedidos_formatados = []
        for pedido in pedidos_resultados:
            data_pedido = datetime.strptime(str(pedido[1]), "%Y-%m-%d").strftime("%d/%m/%Y")
            pedidos_formatados.append((pedido[0], data_pedido, *pedido[2:]))

        valor_total_geral = total_resultado[0] if total_resultado[0] else 0
        total_pedidos = total_resultado[1] if total_resultado[1] else 0

        return pedidos_formatados, valor_total_geral, total_pedidos
    



    
    def exibir_relatorio_cancelado(self, data_inicial, data_final):
        mydb = Conexao.conectar()
        mycursor = mydb.cursor()

        sql = """
            SELECT
                p.id_pedido,
                p.data_pedido,
                p.hora_pedido,
                p.status,
                p.motivo_cancelamento,
                SUM(pp.quantidade * CASE
                    WHEN pp.cod_produto IS NOT NULL THEN pr.preco
                    WHEN pp.id_marmita IS NOT NULL THEN m.preco
                    ELSE 0
                END) AS valor_total
            FROM tb_pedidos p
            LEFT JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE p.data_pedido BETWEEN %s AND %s AND p.status = 'cancelado'
            GROUP BY p.id_pedido
        """

        # Subconsulta para obter o valor total e a quantidade de pedidos cancelados
        sql_total_cancelado = """
            SELECT
                SUM(pp.quantidade * CASE
                    WHEN pp.cod_produto IS NOT NULL THEN pr.preco
                    WHEN pp.id_marmita IS NOT NULL THEN m.preco
                    ELSE 0
                END) AS valor_total_cancelado,
                COUNT(p.id_pedido) AS total_cancelados
            FROM tb_pedidos p
            LEFT JOIN tb_produtos_pedidos pp ON p.id_pedido = pp.id_pedido
            LEFT JOIN tb_produto pr ON pp.cod_produto = pr.cod_produto
            LEFT JOIN tb_marmita m ON pp.id_marmita = m.id_marmita
            WHERE p.data_pedido BETWEEN %s AND %s AND p.status = 'cancelado'
        """

        # Executa a consulta principal para os pedidos cancelados
        mycursor.execute(sql, (data_inicial, data_final))
        cancelados_resultados = mycursor.fetchall()

        # Executa a subconsulta para valores totais dos pedidos cancelados
        mycursor.execute(sql_total_cancelado, (data_inicial, data_final))
        total_cancelado_resultado = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        # Formatação dos dados para o template
        cancelados_formatados = []
        for pedido in cancelados_resultados:
            data_pedido = datetime.strptime(str(pedido[1]), "%Y-%m-%d").strftime("%d/%m/%Y")
            cancelados_formatados.append((pedido[0], data_pedido, *pedido[2:]))

        valor_total_cancelado = total_cancelado_resultado[0] if total_cancelado_resultado[0] else 0
        total_cancelados = total_cancelado_resultado[1] if total_cancelado_resultado[1] else 0

        return cancelados_formatados, valor_total_cancelado, total_cancelados


