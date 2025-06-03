from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from profissionais.models import Profissional
from django.contrib.auth import get_user_model
from .models import Usuario
from django.contrib import messages
from decimal import Decimal, InvalidOperation

def index(request):
    return render(request, "inicio.html")

@login_required
def cadastrar_profissional(request):
    if request.method == "POST":
        # Campos para Usuario
        nome = request.POST.get("nome_completo")
        cpf = request.POST.get("cpf")
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        # Campos para Profissional
        cargo = request.POST.get("cargo")
        gestor = request.POST.get("gestor")
        admissao = request.POST.get("dataAdmissao")
        telefone = request.POST.get("telefone")
        nascimento = request.POST.get("dataNascimento")
        raw_remuneracao = request.POST.get("remuneracao", "")
        try:
            remun_str = raw_remuneracao.replace(".", "").replace(",", ".")
            remuneracao = Decimal(remun_str)
        except InvalidOperation:
            messages.error(request, "Remuneração inválida. Use o formato 2500,00.")
            return redirect("cadastrar")

        if Usuario.objects.filter(cpf=cpf).exists():
            messages.error(request, "Usuário com este CPF já existe.")
            return redirect("cadastrar")

        usuario = Usuario.objects.create_user(
            cpf=cpf,
            password=senha,
            nome_completo=nome,
            email=email,
            is_staff=False
        )

        Profissional.objects.create(
            usuario=usuario,
            cargo=cargo,
            gestor=gestor,
            data_admissao=admissao,
            remuneracao=remuneracao,
            telefone=telefone,
            data_nascimento=nascimento
        )
        messages.success(request, "Usuário cadastrado com sucesso!")
        return redirect("cadastrar")

    return render(request, "cadastro.html")

def login_usuario(request):
    if request.method == "POST":
        cpf = request.POST.get("username")
        senha = request.POST.get("password")
        usuario = authenticate(request, cpf=cpf, password=senha)

        if usuario is not None:
            login(request, usuario)
            return redirect("registrar_ponto")  # nome da rota
        else:
            messages.error(request, "CPF ou senha inválidos.")

    return render(request, "login.html")



def logout_usuario(request):
    logout(request)
    return redirect("login")
