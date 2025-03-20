from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('api/price-changes/', views.price_changes, name='price_changes'),
    # path('api/new-releases/', views.new_releases, name='new_releases'),
    # path('api/generate-config/', views.generate_config, name='generate_config'),
    path('api/search/', views.search, name='search'),
]