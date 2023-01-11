"""Mock API for the Electricity Maps."""

import json

from flask import Flask, request

app = Flask(__name__)


def _generate_electricity_maps_response(zone: str) -> dict:
    """Generate a mock response for the Electricity Maps API."""
    f = open("forecast_de.json", "r")
    data = json.loads(f.read())
    f.close()

    return {
        "zone": zone,
        "forecast": data["forecast"],
        "updatedAt": data["updatedAt"],
    }


@app.route("/carbon-intensity/forecast", methods=["GET"])
def co2_forecast() -> dict:
    """
    Return carbon intensity forecast for a given zone.
    """
    zone = request.args.get("zone")
    token = request.headers.get("X-BLOBR-KEY")
    print(f"token: {token}")
    print(f"zone: {zone}")
    return _generate_electricity_maps_response(zone)


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=4000)
