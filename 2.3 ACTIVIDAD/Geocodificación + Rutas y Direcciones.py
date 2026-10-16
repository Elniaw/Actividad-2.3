import requests
import urllib.parse

# Tu clave de OpenRouteService
key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFkNDgxOTgxMzY3YTRjMzViYjFlYTQ2YzFmNmUwOTU5IiwiaCI6Im11cm11cjY0In0="

def geocoding(location, key):
    while location == "":
        location = input("Enter the location again: ")
        
    geocode_url = "https://api.heigit.org/pelias/v1/search?" 
    url = geocode_url + urllib.parse.urlencode({"text": location, "size": "1"}, safe="")

    headers = {
        'Authorization': key,
        'Accept': 'application/json'
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
        else:
            lat = "null"
            lng = "null"
            new_loc = location
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        
    return json_status, lat, lng, new_loc

# Bucle principal de la aplicación
while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Vehicle profiles available: car, bike, foot")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    
    profile_input = input("Enter a vehicle profile (or 'q' to quit): ").strip().lower()
    if profile_input == "q" or profile_input == "quit":
        break
        
    # Mapeo de perfiles de Graphhopper a OpenRouteService
    profile_map = {
        "car": "driving-car",
        "bike": "cycling-regular",
        "foot": "foot-walking"
    }
    
    if profile_input not in profile_map:
        print("Invalid vehicle profile. Try again.")
        continue
        
    profile = profile_map[profile_input]

    loc1 = input("Starting Location: ")
    if loc1.lower() in ["q", "quit"]:
        break
    status1, lat1, lng1, name1 = geocoding(loc1, key)
    
    loc2 = input("Destination: ")
    if loc2.lower() in ["q", "quit"]:
        break
    status2, lat2, lng2, name2 = geocoding(loc2, key)

    if status1 == 200 and status2 == 200 and lat1 != "null" and lat2 != "null":
        # Llamada a la API de Routing de OpenRouteService
        # ORS espera las coordenadas como 'lon,lat'
        route_url = f"https://api.heigit.org/openrouteservice/v2/directions/{profile}"
        
        params = {
            "api_key": key,
            "start": f"{lng1},{lat1}",
            "end": f"{lng2},{lat2}"
        }
        
        route_reply = requests.get(route_url, params=params)
        route_status = route_reply.status_code
        
        print("=================================================")
        print(f"Routing API Status: {route_status}")
        print(f"Routing API URL:\n{route_reply.url}")
        print("=================================================")
        
        if route_status == 200:
            route_data = route_reply.json()
            features = route_data.get("features", [])
            if len(features) > 0:
                summary = features[0]["properties"]["summary"]
                distance_meters = summary["distance"]
                duration_seconds = summary["duration"]
                
                # Convertir distancia a millas y km
                distance_km = distance_meters / 1000.0
                distance_miles = distance_km * 0.621371
                
                # Convertir duración a formato HH:MM:SS
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                seconds = int(duration_seconds % 60)
                duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                print(f"Directions from {name1} to {name2} by {profile_input}")
                print("=================================================")
                print(f"Distance Traveled: {distance_miles:.1f} miles / {distance_km:.1f} km")
                print(f"Trip Duration: {duration_formatted}")
                print("=================================================")
                
                # Mostrar instrucciones paso a paso (steps)
                segments = features[0]["properties"]["segments"]
                for segment in segments:
                    for step in segment["steps"]:
                        instruction = step["instruction"]
                        step_dist_km = step["distance"] / 1000.0
                        step_dist_miles = step_dist_km * 0.621371
                        print(f"{instruction} ( {step_dist_km:.1f} km / {step_dist_miles:.1f} miles )")
                print("=============================================")
            else:
                print("No route features found.")
        else:
            print("Error retrieving routing data.")
    else:
        print("Error: Could not find valid coordinates for the given locations.")