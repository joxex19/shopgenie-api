# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
import os

app = Flask(__name__)


def scrape_mercadona_products(search_term, max_pages=3):
    driver = Driver(uc=True, headless=True)
    driver.get(f"https://tienda.mercadona.es/search-results?query={search_term}")
    time.sleep(5)

    productos = []
    vistos = set()

    for _ in range(max_pages):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    contenedor_productos = driver.find_elements(By.CSS_SELECTOR, 'div.product-cell[data-testid="product-cell"]')
    print(f"[Mercadona] Productos encontrados: {len(contenedor_productos)}")

    for prod in contenedor_productos:
        try:
            html = prod.get_attribute("innerHTML")
            soup = BeautifulSoup(html, "html.parser")

            nombre_tag = soup.find("h4")
            precio_tag = soup.find("p", {"data-testid": "product-price"})
            img_tag = soup.find("img")

            nombre = nombre_tag.get_text(strip=True) if nombre_tag else None
            precio_str = precio_tag.get_text(strip=True).replace("\u20ac", "").replace(",", ".") if precio_tag else "0"
            imagen = img_tag["src"] if img_tag else None

            if not nombre or nombre in vistos:
                continue
            vistos.add(nombre)

            try:
                precio_float = float(precio_str)
                if precio_float > 10:
                    continue
            except ValueError:
                continue

            productos.append({
                'nombre': nombre,
                'precio': precio_float,
                'supermercado': 'Mercadona',
                'imagen': imagen
            })

        except Exception as e:
            print(f"[Mercadona] Error procesando producto: {e}")

    driver.quit()
    return productos


@app.route("/api/mercadona", methods=["GET"])
def api_mercadona():
    query = request.args.get("productos")
    if not query:
        return jsonify({"error": "Parámetro '?productos=' requerido"}), 400

    terms = [x.strip() for x in query.split(",") if x.strip()]
    resultado = []

    for term in terms:
        print(f"\n🔎 Buscando: {term}")
        resultado.extend(scrape_mercadona_products(term))

    return jsonify(resultado)


if __name__ == "__main__":
    print("\n🚀 API Mercadona corriendo en http://localhost:5000/api/mercadona")
    app.run(debug=True)
