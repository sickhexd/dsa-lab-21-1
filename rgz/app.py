from flask import Flask, request, jsonify

app = Flask(__name__)

# Статический курс валют
rates = {
    "USD": 100.01,
    "EUR": 90.50
}

@app.route('/rate', methods=['GET'])
def get_rate():
    currency = request.args.get('currency')

    if currency not in rates:
        return jsonify({"message": "UNKNOWN CURRENCY"}), 400

    return jsonify({"rate": rates[currency]})

if __name__ == '__main__':
    app.run(debug=True)
