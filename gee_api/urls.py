from django.urls import path
from . import views

urlpatterns = [
    path('village_analysis/<str:village_name>/', views.fetch_village_analysis, name='village_analysis'),
    path('karauli_villages_geojson/', views.karauli_villages_geojson, name='karauli_villages_geojson'), 
    path('get_karauli_raster/', views.get_karauli_raster, name='get_karauli_raster'),
    path('area_change/<str:village_name>/', views.area_change_karauli, name='area_change_karauli')
]
    
