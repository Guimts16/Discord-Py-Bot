import mysql.connector 

conn = mysql.connector.connect(
    user="root",
    password="3141592",
    host="127.0.0.1",
    database="bot",
    auth_plugin='mysql_native_password'
)

def checkConnection():
    global conn
    sql = "select version from rdb$database"

    c = conn.cursor()
    c.execute(sql)
    r = c.fetchall()
    print(f"Version: {r[0][0]}")


def SelectItens():
    global conn
    
    sql = """
        select
        i.nome, 
        i.preco, 
        i.estoque, 
        i.descricao 
        from bot.tbitens i
    """
    c = conn.cursor()
    c.execute(sql)
    return c.fetchall()



if __name__ == "__main__":
    checkConnection()