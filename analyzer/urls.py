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
    path('api/favorite/', views.favorite, name='favorite'),  # 合并添加和删除收藏
    path('api/favorites/', views.favorites_list, name='favorites_list'),

]