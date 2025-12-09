from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)


metrics = PrometheusMetrics(app)


@app.route("/")
def home():
    hostname = os.getenv("HOSTNAME", "desconocido")
    return jsonify({
        "msg": "Aplicación funcionando",
        "hostname": hostname
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

