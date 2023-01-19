"""Mock API for the Green Energy API."""

import json

from flask import Flask, request

app = Flask(__name__)


def _generate_energy_price_response() -> dict:
    """Generate a mock response for the Green Energy API."""
    f = open("forecast_de.json", "r")
    data = json.loads(f.read())
    f.close()

    return {
        "forecast": data["data"],
    }


@app.route("/v1/marketplace", methods=["GET"])
def price_forecast() -> dict:
    """
    Return price forecast for a given zone.
    """
    return _generate_energy_price_response()


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=4000)
