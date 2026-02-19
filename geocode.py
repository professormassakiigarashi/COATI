import googlemaps
import toml

def get_api_key():
    config = toml.load("config.toml")
    return config["google"]["api_key"]

def endereco_para_latlon(endereco):
    api_key = get_api_key()
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(endereco)
    if not geocode_result:
        return None, None
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lon = geocode_result[0]["geometry"]["location"]["lng"]
    return lat, lon