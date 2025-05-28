from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_mercadona_products(search_term):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    search_url = f'https://tienda.mercadona.es/search-results?query={search_term}'
    driver.get(search_url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    results = []
    products = soup.find_all('li', class_='product-cell')
    for product in products:
        name = product.find('h4', class_='subheading')
        price = product.find('p', class_='price')
        if name and price:
            results.append({
                'name': name.text.strip(),
                'price': price.text.strip()
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
    # Este es el cambio clave para Railway:
    app.run(host='0.0.0.0', port=5000)
