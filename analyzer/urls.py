from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.search, name='search'),
    path('api/get_cpu_series/', views.get_cpu_series, name='get_cpu_series'),
    path('api/detail/<str:component_type>/<int:id>/', views.detail, name='detail'),
    path('api/price_stats/', views.price_stats, name='price_stats'),
    path('api/average_price_trend/', views.average_price_trend, name='average_price_trend'),
    path('api/generate_configuration/', views.generate_configuration, name='generate_configuration'),
    # path('api/get_components_by_price/', views.get_components_by_price, name='get_components_by_price'),

]