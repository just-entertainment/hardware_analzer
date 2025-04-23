from django.urls import path
from .views import RegisterView, CustomLoginView, LogoutView, ProfileView, ChangePasswordView, EditProfileView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
]