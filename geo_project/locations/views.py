from rest_framework.response import Response
from rest_framework.views import APIView
from .services import buscar_locais_osm, obter_coordenadas
from django.shortcuts import render
from .models import Local
from django.contrib.gis.geos import Point

def mapa(request):
    return render(request, "locations/map.html")

class BuscarLocaisOSMAPIView(APIView):
    def get(self, request):
        categoria = request.query_params.get("categoria", None)
        endereco = request.query_params.get("endereco", None)
        latitude = request.query_params.get("lat", None)
        longitude = request.query_params.get("lon", None)
        raio = request.query_params.get("raio", "5000")
        
        # Se um endereço for fornecido, converte para latitude/longitude
        if endereco:
            coords = obter_coordenadas(endereco)
            if coords:
                latitude, longitude = coords
            else:
                return Response({"erro": "Não foi possível obter coordenadas para o endereço informado."}, status=400)

        # Valida se latitude e longitude foram definidos
        if not latitude or not longitude:
            return Response({"erro": "Latitude e longitude são obrigatórios"}, status=400)
        
        # Busca locais via Overpass API e salva no banco
        locais = buscar_locais_osm(categoria, latitude, longitude, raio)

        # Também buscar locais já cadastrados no banco dentro do raio
        locais_salvos = Local.objects.filter(
            geom__distance_lte=(Point(float(longitude), float(latitude)), float(raio))
        )

        # Convertendo os locais do banco para JSON
        locais_salvos_json = [
            {
                "id": local.id,
                "nome": local.nome,
                "endereco": local.endereco,
                "latitude": local.geom.y,
                "longitude": local.geom.x,
                "categoria": local.categoria
            }
            for local in locais_salvos
        ]

        return Response({"resultado": locais + locais_salvos_json})
