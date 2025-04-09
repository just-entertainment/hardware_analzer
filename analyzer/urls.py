from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.search, name='search'),
    path('api/get_cpu_series/', views.get_cpu_series, name='get_cpu_series'),
    path('api/detail/<str:component_type>/<int:id>/', views.detail, name='detail'),
    path('api/price_stats/', views.price_stats, name='price_stats'),
]