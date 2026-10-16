from flask import Flask, render_template, request
import requests

app = Flask(__name__)

KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFkNDgxOTgxMzY3YTRjMzViYjFlYTQ2YzFmNmUwOTU5IiwiaCI6Im11cm11cjY0In0="

def get_coords(location):
    # Si el usuario pone nombres cortos, ayudamos a Nominatim a buscar en Chile por defecto
    search_query = location
    if "chile" not in location.lower():
        search_query = f"{location}, Chile"
        
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'CiscoLabApp/2.0'}
    params = {"q": search_query, "format": "json", "limit": 1}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 0:
                lat = float(data[0]["lat"])
                lng = float(data[0]["lon"])
                name = data[0]["display_name"]
                print(f"✅ Encontrado: {name} -> Lat: {lat}, Lng: {lng}")
                return lat, lng, name
    except Exception as e:
        print(f"❌ Error en geocodificación: {e}")
        
    return None, None, None

@app.route("/", methods=["GET", "POST"])
def index():
    route_info = None
    coords_path = []
    
    if request.method == "POST":
        loc1 = request.form.get("loc1")
        loc2 = request.form.get("loc2")
        profile = request.form.get("profile", "driving-car")
        
        print(f"\n--- NUEVA PETICIÓN ---")
        lat1, lng1, name1 = get_coords(loc1)
        lat2, lng2, name2 = get_coords(loc2)
        
        if lat1 is not None and lat2 is not None:
            # Ampliamos el radio a 50km (50000m) para evitar que falle por puntos lejanos a carreteras
            params = {
                "api_key": KEY,
                "start": f"{lng1},{lat1}",
                "end": f"{lng2},{lat2}",
                "radiuses": "50000,50000"
            }
            
            # Intento 1 con el perfil elegido
            route_url = f"https://api.heigit.org/openrouteservice/v2/directions/{profile}"
            r = requests.get(route_url, params=params, timeout=10)
            
            # Si falla, respaldo automático a modo peatonal
            if r.status_code != 200:
                print("⚠️ Ruta principal falló, aplicando respaldo a modo caminante...")
                route_url = "https://api.heigit.org/openrouteservice/v2/directions/foot-walking"
                r = requests.get(route_url, params=params, timeout=10)

            if r.status_code == 200:
                r_data = r.json()
                features = r_data.get("features", [])
                if features:
                    summary = features[0]["properties"]["summary"]
                    geometry = features[0]["geometry"]["coordinates"]
                    # Invertimos las coordenadas de [lng, lat] a [lat, lng] para Leaflet.js
                    coords_path = [[pt[1], pt[0]] for pt in geometry]
                    print(f"🎉 ¡Ruta dibujada con éxito en el mapa!")
                    
                    route_info = {
                        "distance_km": round(summary["distance"] / 1000.0, 2),
                        "duration_min": round(summary["duration"] / 60.0, 1),
                        "name1": name1,
                        "name2": name2
                    }
                else:
                    print("⚠️ La API respondió pero la ruta vino vacía.")
            else:
                print(f"❌ Error de ruteo final: {r.text}")
        else:
            print("❌ No se pudieron obtener coordenadas válidas.")
                        
    return render_template("index.html", route_info=route_info, coords_path=coords_path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)