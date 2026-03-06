import json
import requests
import traceback
from solar_calc import calculate_solar, calculate_roi

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

def handler(event, context):
    try:
        if event.get('method') != 'POST':
            return {
                "statusCode": 405,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                },
                "body": json.dumps({"error": "Method not allowed"})
            }

        body = event.get('body', '{}')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body

        lat = data.get("lat")
        lng = data.get("lng")
        roof_area = data.get("roof_area")

        if lat is None or lng is None:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                },
                "body": json.dumps({"error": "Lat/Lng missing"})
            }

        if roof_area is None:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                },
                "body": json.dumps({"error": "Roof area missing"})
            }

        # Convert roof_area to float (frontend may send string)
        try:
            roof_area = float(roof_area)
        except Exception as e:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                },
                "body": json.dumps({"error": "Invalid roof_area", "details": str(e)})
            }

        irradiance, err = get_irradiance(lat, lng)

        if err:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                },
                "body": json.dumps({"error": "Irradiance API failed", "details": err})
            }

        # Ensure irradiance is numeric
        try:
            irradiance = float(irradiance)
        except Exception:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
                },
                "body": json.dumps({"error": "Invalid irradiance value", "details": str(irradiance)})
            }

        annual_energy, annual_savings = calculate_solar(roof_area, irradiance)
        payback, lifetime_savings = calculate_roi(annual_energy)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            },
            "body": json.dumps({
                "irradiance": irradiance,
                "annual_energy_kwh": annual_energy,
                "annual_savings_inr": annual_savings,
                "payback_years": payback,
                "lifetime_savings_inr": lifetime_savings
            })
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            },
            "body": json.dumps({"error": "Backend crashed", "details": str(e)})
        }