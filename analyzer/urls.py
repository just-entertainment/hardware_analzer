from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.search, name='search'),
    path('api/detail/<str:component_type>/<int:id>/', views.detail, name='detail'),
]