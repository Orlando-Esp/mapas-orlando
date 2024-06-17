from flask import Flask, request, render_template
import googlemaps
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = 'AIzaSyArVLxNeIn0qVaDgGNNcqsp2YgLe96e-gw'
gmaps = googlemaps.Client(key=API_KEY)

def obtener_ruta(origen, destino, paradas):
    ahora = datetime.now()
    ruta = gmaps.directions(origen,
                            destino,
                            waypoints=paradas,
                            mode="driving",
                            departure_time=ahora,
                            traffic_model="best_guess")
    return ruta

def calcular_consumo_combustible(distancia_km, eficiencia_km_por_l):
    return distancia_km / eficiencia_km_por_l

def convertir_duracion(duracion_segundos):
    horas = duracion_segundos // 3600
    minutos = (duracion_segundos % 3600) // 60
    return f"{int(horas)} horas y {int(minutos)} minutos"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ruta', methods=['POST'])
def mostrar_ruta():
    origen = request.form['origen']
    destino = request.form['destino']
    paradas = [p.strip() for p in request.form['paradas'].split(',')]
    
    ruta_gmaps = obtener_ruta(origen, destino, paradas)
    
    eficiencia_km_por_l = 12  
    
    distancia_total_gmaps = sum(leg['distance']['value'] for leg in ruta_gmaps[0]['legs']) / 1000
    consumo_combustible_gmaps = calcular_consumo_combustible(distancia_total_gmaps, eficiencia_km_por_l)
    
    duracion_total_segundos = sum(leg['duration']['value'] for leg in ruta_gmaps[0]['legs'])
    duracion_total = convertir_duracion(duracion_total_segundos)
    
    llegada_estimada = datetime.now() + timedelta(seconds=sum(leg.get('duration_in_traffic', leg['duration'])['value'] for leg in ruta_gmaps[0]['legs']))
    
    return render_template('ruta.html', 
                           ruta_gmaps=ruta_gmaps,
                           consumo_combustible_gmaps=consumo_combustible_gmaps,
                           distancia_total_gmaps=distancia_total_gmaps,
                           duracion_total=duracion_total,
                           llegada_estimada=llegada_estimada.strftime("%Y-%m-%d %H:%M:%S"),
                           waypoints=paradas)

if __name__ == '__main__':
    app.run(debug=True)
