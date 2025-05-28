# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)


def scrape_mercadona_products(search_term):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    url = f"https://tienda.mercadona.es/search-results?query={search_term}"
    res = requests.get(url, headers=headers)

    productos = []
    vistos = set()

    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.select('div.product-cell[data-testid="product-cell"]')

        for prod in cards:
            nombre_tag = prod.find("h4")
            precio_tag = prod.find("p", {"data-testid": "product-price"})
            img_tag = prod.find("img")

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

