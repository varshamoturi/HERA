import requests
def get_google_maps_listings(api_key, query, location="San Francisco", radius=10000):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "location": location,
        "radius": radius,
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        print("Error:", data.get("error_message", "Unknown error"))
        return []




