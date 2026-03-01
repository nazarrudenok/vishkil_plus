import pymysql

bot = '8355675288:AAGjeACTPhZfOGfYjTJeF9M2xFWOs4jkhZY'

host = "crossover.proxy.rlwy.net"
port = 14501
user = "root"
password = "ZcwcQvUHPyezOfkDLPINEdEEjiugrukw"
database = "railway"

connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=port
)

cursor = connection.cursor()

# cursor.execute("DROP TABLE users")
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT, username VARCHAR(100), poz VARCHAR(32), sex VARCHAR(32), num VARCHAR(32), chat_id BIGINT, firstname VARCHAR(100), lastname VARCHAR(100), PRIMARY KEY (ID))")
connection.commit()