from django.urls import path
from . import views
from .views import favorite_delete, favorite

app_name = 'analyzer'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.search, name='search'),
    path('api/get_cpu_series/', views.get_cpu_series, name='get_cpu_series'),
    path('api/detail/<str:component_type>/<int:id>/', views.detail, name='detail'),
    path('api/price_stats/', views.price_stats, name='price_stats'),
    path('api/average_price_trend/', views.average_price_trend, name='average_price_trend'),
    path('api/generate_configuration/', views.generate_configuration, name='generate_configuration'),
    path('api/favorite/', favorite, name='favorite'),
    path('api/favorite/', favorite_delete, name='favorite_delete'),
    path('api/favorite/delete/', favorite_delete, name='favorite_delete'),


]