import requests
from django.contrib.gis.geos import Point
from .models import Local

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Mapeamento de categorias OSM para nossa API
CATEGORIAS_OSM = {
    "restaurant": "amenity=restaurant",
    "cafe": "amenity=cafe",
    "hotel": "tourism=hotel",
    "hospital": "amenity=hospital",
    "park": "leisure=park",
    "supermarket": "shop=supermarket"
}

def obter_coordenadas(endereco):
    url = f"https://nominatim.openstreetmap.org/search?q={endereco}&format=json"
        
    try:
        response = requests.get(url, headers={"User-Agent": "geo_app"})
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            return None
        
        # Tenta converter a resposta para JSON
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print("Erro ao decodificar JSON da API")
            return None

        if not data:
            print("Nenhum resultado encontrado para o endereço.")
            return None

        lat = data[0]["lat"]
        lon = data[0]["lon"]
        return lat, lon

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def buscar_locais_osm(categoria, latitude, longitude, raio=5000):
    """
    Busca locais no OpenStreetMap via Overpass API e armazena no PostGIS.
    """
    if categoria not in CATEGORIAS_OSM:
        return f"Categoria '{categoria}' não suportada. Use uma das seguintes: {list(CATEGORIAS_OSM.keys())}"

    query = f"""
    [out:json];
    node[{CATEGORIAS_OSM[categoria]}](around:{raio},{latitude},{longitude});
    out;
    """
    
    response = requests.get(OVERPASS_URL, params={"data": query})
    data = response.json()

    if "elements" not in data:
        return "Nenhum dado encontrado."

    locais_adicionados = []

    for place in data["elements"]:
        nome = place.get("tags", {}).get("name", "Sem Nome")
        endereco = place.get("tags", {}).get("addr:street", "Endereço desconhecido")
        lat = place["lat"]
        lon = place["lon"]

        # Salvar no banco de dados (PostGIS)
        local, created = Local.objects.get_or_create(
            nome=nome,
            endereco=endereco,
            categoria=categoria,
            cidade="Desconhecido",
            estado="Desconhecido",
            geom=Point(lon, lat)
        )

        locais_adicionados.append({
            "id": local.id,
            "nome": local.nome,
            "endereco": local.endereco,
            "latitude": lat,
            "longitude": lon,
            "categoria": categoria
        })

    return locais_adicionados
