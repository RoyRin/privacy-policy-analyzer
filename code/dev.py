"""Local dev server — serves static files + API."""
from api.index import app
import os

@app.route("/")
def home():
    with open(os.path.join(os.path.dirname(__file__), "public", "index.html")) as f:
        return f.read()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
