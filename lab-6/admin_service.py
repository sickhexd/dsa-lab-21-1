from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# Параметры подключения к базе данных
DB_NAME = "lab6"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

@app.route('/admins', methods=['GET'])
def get_admins():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM admins")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Преобразуем в список строк
        admins = [str(row[0]) for row in rows]
        return jsonify({"admins": admins}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5003)
