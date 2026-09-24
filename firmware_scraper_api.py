from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os


app = Flask(__name__)


def scrape_page(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1366,
                "height": 768
            }
        )

        try:

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(2000)

            result = {
                "url": url,
                "status": response.status if response else None,
                "final_url": page.url,
                "title": page.title(),
                "content": page.locator("body").inner_text()
            }

            return result

        finally:

            page.close()
            browser.close()


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok"
    })


@app.route("/scrape", methods=["POST"])
def scrape():

    data = request.get_json(silent=True) or {}

    url = data.get("url")

    if not url:

        return jsonify({
            "error": "Missing url"
        }), 400

    try:

        result = scrape_page(url)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "url": url,
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8000))

    print("Firmware scraper API starting...")
    print(f"Port: {port}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        threaded=False
    )