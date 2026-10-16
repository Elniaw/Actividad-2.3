from flask import Flask, render_template, request
import requests

app = Flask(__name__)

KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImFkNDgxOTgxMzY3YTRjMzViYjFlYTQ2YzFmNmUwOTU5IiwiaCI6Im11cm11cjY0In0="

def get_coords(location):
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
                return lat, lng, name
    except Exception as e:
        print(f"❌ Error en geocodificación: {e}")
        
    return None, None, None

@app.route("/", methods=["GET", "POST"])
def index():
    route_info = None
    coords_path = []
    error_msg = None
    
    if request.method == "POST":
        loc1 = request.form.get("loc1")
        loc2 = request.form.get("loc2")
        profile = request.form.get("profile", "driving-car")
        engine_type = request.form.get("engine", "1.6")
        
        lat1, lng1, name1 = get_coords(loc1)
        lat2, lng2, name2 = get_coords(loc2)
        
        if lat1 is not None and lat2 is not None:
            params = {
                "api_key": KEY,
                "start": f"{lng1},{lat1}",
                "end": f"{lng2},{lat2}",
                "radiuses": "50000,50000"
            }
            
            try:
                route_url = f"https://api.heigit.org/openrouteservice/v2/directions/{profile}"
                r = requests.get(route_url, params=params, timeout=10)
                
                if r.status_code != 200:
                    route_url = "https://api.heigit.org/openrouteservice/v2/directions/foot-walking"
                    r = requests.get(route_url, params=params, timeout=10)

                if r.status_code == 200:
                    r_data = r.json()
                    features = r_data.get("features", [])
                    if features:
                        summary = features[0]["properties"]["summary"]
                        geometry = features[0]["geometry"]["coordinates"]
                        coords_path = [[pt[1], pt[0]] for pt in geometry]
                        
                        dist_km = summary["distance"] / 1000.0
                        duration_min = summary["duration"] / 60.0
                        
                        rendimiento_map = {
                            "1.0": 16.0, "1.4": 14.0, "1.6": 12.5,
                            "1.6t": 10.5, "2.0": 9.5, "v8": 5.0
                        }
                        rendimiento = rendimiento_map.get(engine_type, 12.0)
                        litros_consumidos = dist_km / rendimiento
                        costo_bencina = int(litros_consumidos * 1300)
                        
                        route_info = {
                            "distance_km": round(dist_km, 2),
                            "duration_min": round(duration_min, 1),
                            "name1": name1,
                            "name2": name2,
                            "engine_label": engine_type,
                            "costo_bencina": f"${costo_bencina:,}".replace(",", ".")
                        }
                    else:
                        error_msg = "La API no encontró una ruta conectada entre estos dos puntos (muy lejos o separados por mar)."
                else:
                    error_msg = "Error al calcular la ruta. Es posible que la distancia sea demasiado extrema para la API."
            except Exception as e:
                error_msg = f"Error de conexión con el servicio de mapas: {str(e)}"
        else:
            error_msg = "No se pudieron encontrar las coordenadas de una o ambas ubicaciones. Intenta ser más específico."
                        
    return render_template("index.html", route_info=route_info, coords_path=coords_path, error_msg=error_msg)

if __name__ == "__main__":
    app.run(debug=True, port=5000)