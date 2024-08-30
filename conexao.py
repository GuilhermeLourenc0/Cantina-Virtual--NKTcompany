import mysql.connector

class Conexao:

    def conectar():
        mydb = mysql.connector.connect(
            user="root",
            password="root",
            host="localhost",
            database="cantina"
        )
        
        return mydb