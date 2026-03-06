from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback
from solar_calc import calculate_solar, calculate_roi

app = Flask(__name__)
CORS(app)

@app.route("/debug", methods=["GET"])
def debug_endpoint():
    return jsonify({"message": "Backend running OK"})


def get_irradiance(lat, lng):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lng}&daily=shortwave_radiation_sum&timezone=auto"
        )

        print("\nOpen-Meteo Request:", url)

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        print("API Status:", response.status_code)

        data = response.json()
        irr = data["daily"]["shortwave_radiation_sum"][0]

        print("Irradiance:", irr)
        return irr, None

    except Exception as e:
        traceback.print_exc()
        return None, str(e)


@app.route("/calculate-location", methods=["POST"])
def calculate_location():
    try:
        data = request.get_json()

        lat = data.get("lat")
        lng = data.get("lng")
        roof_area = data.get("roof_area")

        if lat is None or lng is None:
            return jsonify({"error": "Lat/Lng missing"}), 400

        if roof_area is None:
            return jsonify({"error": "Roof area missing"}), 400

        # Convert roof_area to float (frontend may send string)
        try:
            roof_area = float(roof_area)
        except Exception as e:
            return jsonify({"error": "Invalid roof_area", "details": str(e)}), 400

        irradiance, err = get_irradiance(lat, lng)

        if err:
            return jsonify({"error": "Irradiance API failed", "details": err}), 500

        # Ensure irradiance is numeric
        try:
            irradiance = float(irradiance)
        except Exception:
            return jsonify({"error": "Invalid irradiance value", "details": str(irradiance)}), 500

        annual_energy, annual_savings = calculate_solar(roof_area, irradiance)
        payback, lifetime_savings = calculate_roi(annual_energy)

        return jsonify({
            "irradiance": irradiance,
            "annual_energy_kwh": annual_energy,
            "annual_savings_inr": annual_savings,
            "payback_years": payback,
            "lifetime_savings_inr": lifetime_savings
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Backend crashed", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
