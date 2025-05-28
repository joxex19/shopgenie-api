from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/mercadona', methods=['GET'])
def api_mercadona():
    term = request.args.get('q')
    if not term:
        return jsonify({'error': 'Missing search term'}), 400

    try:
        url = f"https://tienda.mercadona.es/api/search/?query={term}"
        response = requests.get(url)
        data = response.json()

        products = []
        for item in data.get('results', []):
            products.append({
                'name': item.get('display_name'),
                'price': item.get('price_instructions', {}).get('unit_price')
            })

        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

