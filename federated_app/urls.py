from django.urls import path
from . import views

urlpatterns = [
    # Navegación y autenticación de médicos
    path('', views.dashboard_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Endpoints de la API federada (autenticados con API Key de hospital)
    path('api/modelo/', views.api_obtener_modelo, name='api_modelo'),
    path('api/actualizaciones/', views.api_enviar_actualizacion, name='api_actualizaciones'),

    # Herramientas de apoyo médico y simulación
    path('api/diagnosticar/', views.api_diagnosticar, name='api_diagnosticar'),
    path('api/simular-ronda/', views.api_simular_ronda, name='api_simular_ronda'),
]
