from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def scrape_mercadona_products(search_term, max_pages=2):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(f"https://tienda.mercadona.es/search-results?query={search_term}")
    time.sleep(5)

    productos = []
    vistos = set()

    for _ in range(max_pages):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    elementos = driver.find_elements(By.CSS_SELECTOR, 'div.product-cell[data-testid="product-cell"]')
    for el in elementos:
        html = el.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")

        nombre_tag = soup.find("h4")
        precio_tag = soup.find("p", {"data-testid": "product-price"})
        img_tag = soup.find("img")

        nombre = nombre_tag.get_text(strip=True) if nombre_tag else None
        precio_str = precio_tag.get_text(strip=True).replace("€", "").replace(",", ".") if precio_tag else "0"
        imagen = img_tag["src"] if img_tag else None

        if not nombre or nombre in vistos:
            continue
        vistos.add(nombre)

        try:
            precio_float = float(precio_str)
            if precio_float > 10:  # Evita precios raros
                continue
        except ValueError:
            continue

        productos.append({
            "nombre": nombre,
            "precio": precio_float,
            "supermercado": "Mercadona",
            "imagen": imagen
        })

    driver.quit()
    return productos


@app.route("/api/mercadona", methods=["GET"])
def api_mercadona():
    query = request.args.get("productos")
    if not query:
        return jsonify({"error": "Falta el parámetro '?productos='"}), 400

    terms = [x.strip() for x in query.split(",") if x.strip()]
    resultado = []
    for term in terms:
        resultado.extend(scrape_mercadona_products(term))

    return jsonify(resultado)


if __name__ == "__main__":
    print("🚀 API de Mercadona lista en http://localhost:5000/api/mercadona")
    app.run(host="0.0.0.0", port=5000)

