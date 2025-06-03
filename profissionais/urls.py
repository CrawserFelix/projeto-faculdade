from django.urls import path
from . import views

urlpatterns = [
    path('registrarponto/', views.registrar_ponto, name='registrar_ponto'),
    path('folhadeponto/', views.folha_de_ponto, name='folha_de_ponto'),
]
