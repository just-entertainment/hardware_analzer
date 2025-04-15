from django.urls import path
from . import views
from django.urls import path
from accounts.views import login_view
from analyzer.views import index

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('accounts/login/', login_view, name='login'),
]