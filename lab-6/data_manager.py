from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "currencies.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# GET /convert?currency_name=USD&amount=100
@app.route('/convert', methods=['GET'])
def convert_currency():
    currency_name = request.args.get("currency_name")
    amount = request.args.get("amount")

    if not currency_name or not amount:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Amount must be a number"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT rate FROM currencies WHERE currency_name = ?", (currency_name.upper(),))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return jsonify({"error": "Currency not found"}), 404

        rate = float(result["rate"])
        converted = round(amount * rate, 3)

        return jsonify({
            "currency_name": currency_name.upper(),
            "amount": amount,
            "converted_to_rub": converted
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET /currencies
@app.route('/currencies', methods=['GET'])
def get_currencies():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
        rows = cursor.fetchall()
        conn.close()

        data = [{"currency_name": row["currency_name"], "rate": float(row["rate"])} for row in rows]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5002)
