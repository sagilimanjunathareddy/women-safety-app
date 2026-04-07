# utils/location_tracker.py
import requests

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data.get("loc", "0,0")
        city = data.get("city", "Unknown")
        region = data.get("region", "")
        return {
            "latitude": loc.split(',')[0],
            "longitude": loc.split(',')[1],
            "address": f"{city}, {region}"
        }
    except Exception as e:
        print(f"⚠️ Location error: {e}")
        return {"latitude": "0", "longitude": "0", "address": "Unavailable"}
