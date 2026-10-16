import requests
import urllib.parse

# Tu clave/token de OpenRouteService
key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFkNDgxOTgxMzY3YTRjMzViYjFlYTQ2YzFmNmUwOTU5IiwiaCI6Im11cm11cjY0In0="

def geocoding(location, key):
    while location == "":
        location = input("Enter the location again: ")
        
    geocode_url = "https://api.heigit.org/pelias/v1/search?" 
    url = geocode_url + urllib.parse.urlencode({"text": location, "size": "1"}, safe="")

    headers = {
        'Authorization': key,
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
    }

    replydata = requests.get(url, headers=headers)
    json_status = replydata.status_code
    
    if json_status == 200:
        json_data = replydata.json()
        if len(json_data.get("features", [])) > 0:
            coords = json_data["features"][0]["geometry"]["coordinates"]
            lng = coords[0]
            lat = coords[1]
            
            properties = json_data["features"][0]["properties"]
            name = properties.get("name", location)
            country = properties.get("country", "")
            region = properties.get("region", "")
            
            if region and country:
                new_loc = f"{name}, {region}, {country}"
            elif country:
                new_loc = f"{name}, {country}"
            else:
                new_loc = name
                
            print(f"Geocoding API URL for {new_loc}\n{url}")
        else:
            lat = "null"
            lng = "null"
            new_loc = location
            print(f"Geocode API status: {json_status}\nError message: No results found for {location}")
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        print(f"Geocode API status: {json_status}\nError message: Invalid credentials or request.")
        
    return json_status, lat, lng, new_loc

while True:
    loc1 = input("Starting Location (or type 'q' to quit): ")
    if loc1.lower() == "quit" or loc1.lower() == "q":
        break
    orig = geocoding(loc1, key)
    print("Orig Coord Tuple:", orig)
    
    loc2 = input("Destination (or type 'q' to quit): ")
    if loc2.lower() == "quit" or loc2.lower() == "q":
        break
    dest = geocoding(loc2, key)
    print("Dest Coord Tuple:", dest)
    print("-" * 50)