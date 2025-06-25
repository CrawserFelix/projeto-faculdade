'''from django.urls import path
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
    path('profissionais/excluir/<int:profissional_id>/', views.excluir_profissional, name='excluir_profissional'),

    # Folhas de ponto
    path('folha/<int:profissional_id>/', views.visualizar_folha, name='visualizar_folha'),
    path('folhas/', views.listar_folhas, name='listar_folhas'),
    path('folha/<int:profissional_id>/salvar/', views.salvar_alteracoes_folha, name='salvar_alteracoes_folha'),
    
    # Chat 
    path('chat/gestor/', views.chat_gestor, name='chat_gestor'),
    path('chat/gestor/<int:profissional_id>/', views.chat_gestor, name='chat_gestor_conversa'),
    path('chat/', views.chat_profissional, name='chat'),
]
'''
from django.urls import path
from . import views

urlpatterns = [
    # Home + autenticação
    path('', views.index, name='inicio'),
    path('login/',  views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Registro de ponto
    path('registrar/', views.registrar_ponto, name='registrar_ponto'),

    # Profissionais
    path('profissionais/', views.listar_profissionais, name='listar_profissionais'),
    path('profissionais/novo/', views.cadastrar_profissional, name='cadastrar_profissional'),
    path('profissionais/editar/<int:profissional_id>/', views.editar_profissional, name='editar_profissional'),
    path('profissionais/excluir/<int:profissional_id>/', views.excluir_profissional, name='excluir_profissional'),

    # Folhas de ponto
    path('folhas/', views.listar_folhas, name='listar_folhas'),
    path('folhas/<int:profissional_id>/', views.visualizar_folha, name='visualizar_folha'),
    path('folhas/<int:profissional_id>/salvar/', views.salvar_alteracoes_folha, name='salvar_alteracoes_folha'),

    # Chat
    path('chat/', views.chat_profissional, name='chat'),
    path('chat/gestor/', views.chat_gestor, name='chat_gestor'),
    path('chat/gestor/<int:profissional_id>/', views.chat_gestor, name='chat_gestor_conversa'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
]
