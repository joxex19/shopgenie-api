from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def scrape_mercadona_products(search_term):
    url = "https://tienda.mercadona.es/api/products/search"
    params = {"query": search_term}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise Exception("Mercadona API no disponible")

    data = response.json()
    results = []

    for item in data.get("results", []):
        product = item.get("display_name", "")
        price = item.get("price_instructions", {}).get("unit_price", "")
        if product and price:
            results.append({
                "name": product,
                "price": f"{price} €"
            })

    return results

@app.route('/api/mercadona', methods=['GET'])
def api_mercadona():
    term = request.args.get('q')
    if not term:
        return jsonify({'error': 'Missing search term'}), 400

    try:
        result = scrape_mercadona_products(term)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

