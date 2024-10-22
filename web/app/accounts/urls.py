from django.urls import path
from .views import HomeView, RegistrationFormView, CustomTokenObtainPairView, LogoutView, AdminUserListView

app_name = 'accounts'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegistrationFormView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('users/', AdminUserListView.as_view(), name='users-list'),
    path('users/<int:pk>/', AdminUserListView.as_view(), name='user-detail')
]
