import googlemaps

def endereco_para_latlon(endereco):
    gmaps = googlemaps.Client(key='AIzaSyBFbdTjp0MccgWj8yhkQcHS6__dEWraE_I')
    geocode_result = gmaps.geocode(endereco)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lon = geocode_result[0]["geometry"]["location"]["lng"]
    return lat, lon