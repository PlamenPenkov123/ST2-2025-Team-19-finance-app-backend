from django.urls import path

from . import views

urlpatterns = [
    path('register', views.registerUser, name='register'),
    path('login', views.loginUser, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('logout_all', views.logoutAllSessions, name='logout_all'),
    path('profile', views.getCurrentUser, name='profile'),
    path('profile/update', views.updateUser, name='update_profile'),
]