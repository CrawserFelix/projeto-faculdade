from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrar/', views.cadastrar_profissional, name='cadastrar'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
]
