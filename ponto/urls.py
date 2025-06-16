from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='inicio'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Registro de ponto
    path('registrar/', views.registrar_ponto, name='registrar_ponto'),

    # Profissionais
    path('profissionais/', views.listar_profissionais, name='listar_profissionais'),
    path('profissionais/novo/', views.cadastrar_profissional, name='cadastrar'),
    path('profissionais/editar/<int:profissional_id>/', views.editar_profissional, name='editar_profissional'),
    path('chat/', views.chat, name='chat'),

    # Folhas de ponto
    path('folha/<int:profissional_id>/', views.visualizar_folha, name='visualizar_folha'),
    path('folhas/', views.listar_folhas, name='listar_folhas'),
    path('folha/<int:profissional_id>/salvar/', views.salvar_alteracoes_folha, name='salvar_alteracoes_folha'),
]

