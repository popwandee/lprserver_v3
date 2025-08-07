def get_location():
    try:
        response = requests.get("http://ip-api.com/json/")
        location = response.json()
        logging.debug(f"🌍 Location from ip-api.com: {location['lat']}, {location['lon']} "
                      f"({location['city']}, {location['regionName']}, {location['country']})")
        
        location = f"{location['lat']}, {location['lon']}"
    except requests.RequestException as e:
        logging.debug(f"❌ Unable to fetch location: {e}. Using coordinates 0, 0 instead.")
        location = f"0,0"
    return location