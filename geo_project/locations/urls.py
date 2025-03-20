from django.urls import path
from .views import BuscarLocaisOSMAPIView, mapa

urlpatterns = [
    path("", mapa, name="mapa"),  # Página do mapa
    path("buscar-locais/", BuscarLocaisOSMAPIView.as_view(), name="buscar_locais_osm"),
]