import pymysql

bot = '8355675288:AAGjeACTPhZfOGfYjTJeF9M2xFWOs4jkhZY'

connection = pymysql.connect(
    host="switchyard.proxy.rlwy.net",
    user="root",
    password="WqleWxZfmJxQQQJxCmqlfbsKElUUYztG",
    database="railway",
    port=47846,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

cursor = connection.cursor()

# cursor.execute("DROP TABLE users")
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT, username VARCHAR(100), poz VARCHAR(32), sex VARCHAR(32), num VARCHAR(32), chat_id BIGINT, firstname VARCHAR(100), lastname VARCHAR(100), PRIMARY KEY (ID))")
connection.commit()