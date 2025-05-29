from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "currencies.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# POST /load
@app.route('/load', methods=['POST'])
def load_currency():
    data = request.json
    currency_name = data.get("currency_name")
    rate = data.get("rate")

    if not currency_name or rate is None:
        return jsonify({"error": "Missing currency_name or rate"}), 400

    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({"error": "Rate must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Rate must be a number"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM currencies WHERE currency_name = ?", (currency_name.upper(),))
        existing = cursor.fetchone()

        if existing:
            return jsonify({"message": "Currency already exists"}), 409

        cursor.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (?, ?)",
            (currency_name.upper(), rate)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Currency loaded successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST /update_currency
@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.json
    currency_name = data.get("currency_name")
    rate = data.get("rate")

    if not currency_name or rate is None:
        return jsonify({"error": "Missing currency_name or rate"}), 400

    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({"error": "Rate must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Rate must be a number"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM currencies WHERE currency_name = ?", (currency_name.upper(),))
        existing = cursor.fetchone()

        if not existing:
            return jsonify({"error": "Currency not found"}), 404

        cursor.execute(
            "UPDATE currencies SET rate = ? WHERE currency_name = ?",
            (rate, currency_name.upper())
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Currency updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST /delete
@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.json
    currency_name = data.get("currency_name")

    if not currency_name:
        return jsonify({"error": "Missing currency_name"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM currencies WHERE currency_name = ?", (currency_name.upper(),))
        existing = cursor.fetchone()

        if not existing:
            return jsonify({"error": "Currency not found"}), 404

        cursor.execute("DELETE FROM currencies WHERE currency_name = ?", (currency_name.upper(),))
        conn.commit()
        conn.close()

        return jsonify({"message": "Currency deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
