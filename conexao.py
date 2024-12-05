import mysql.connector

class Conexao:

    def conectar():
        mydb = mysql.connector.connect(
            user="cantina",
            password="988430466Tel",
            host="cantina-virtual.mysql.database.azure.com",
            database="bd_cantinadalu"
        )
        
        return mydb