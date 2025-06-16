# ponto/views.py refatorado (completo)
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, datetime
from calendar import monthrange
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import Profissional, Usuario, RegistroPonto, Mensagem


def index(request):
    return render(request, "ponto/inicio.html")


def login_usuario(request):
    if request.method == "POST":
        cpf = request.POST.get("username")
        senha = request.POST.get("password")
        usuario = authenticate(request, cpf=cpf, password=senha)

        if usuario is not None:
            login(request, usuario)
            return redirect("inicio")
        else:
            messages.error(request, "CPF ou senha inválidos.")

    return render(request, "ponto/login.html")


def logout_usuario(request):
    logout(request)
    return redirect("login")


@login_required
def cadastrar_profissional(request):
    if request.user.is_staff:
        if request.method == "POST":
            cpf = request.POST.get("cpf").replace(".", "").replace("-", "")
            nome = request.POST.get("nomeCompleto")
            email = request.POST.get("email")
            senha = request.POST.get("senha")
            telefone = request.POST.get("telefone")
            data_nascimento = request.POST.get("dataNascimento")
            remuneracao = request.POST.get("remuneracao").replace(".", "").replace(",", ".")
            data_admissao = request.POST.get("dataAdmissao")
            entrada = request.POST.get("horarioEntrada")
            intervalo_inicio = request.POST.get("intervaloInicio")
            intervalo_fim = request.POST.get("intervaloFim")
            saida = request.POST.get("horarioSaida")

            if Usuario.objects.filter(cpf=cpf).exists():
                messages.error(request, "Usuário com esse CPF já existe.")
                return redirect("cadastrar")

            usuario = Usuario.objects.create_user(
                cpf=cpf,
                nome_completo=nome,
                email=email,
                password=senha
            )

            Profissional.objects.create(
                usuario=usuario,
                telefone=telefone,
                data_nascimento=data_nascimento,
                remuneracao=remuneracao,
                data_admissao=data_admissao,
                horario_entrada=entrada,
                intervalo_inicio=intervalo_inicio,
                intervalo_fim=intervalo_fim,
                horario_saida=saida
            )

            messages.success(request, "Profissional cadastrado com sucesso.")
            return redirect("listar_profissionais")

        return render(request, "ponto/cadastro.html", {"modo_gestor": True})

    else:
        try:
            profissional = Profissional.objects.get(usuario=request.user)
        except Profissional.DoesNotExist:
            profissional = None

        return render(request, "ponto/cadastro.html", {
            "modo_gestor": False,
            "profissional": profissional
        })


@login_required
def listar_profissionais(request):
    profissionais = Profissional.objects.select_related("usuario").all()
    return render(request, "ponto/lista.html", {"profissionais": profissionais})


@user_passes_test(lambda u: u.is_staff)
def editar_profissional(request, profissional_id):
    profissional = get_object_or_404(Profissional, id=profissional_id)
    usuario = profissional.usuario

    if request.method == "POST":
        usuario.nome_completo = request.POST.get("nomeCompleto")
        usuario.email = request.POST.get("email")
        usuario.save()

        profissional.telefone = request.POST.get("telefone")
        profissional.data_nascimento = request.POST.get("dataNascimento")
        profissional.remuneracao = request.POST.get("remuneracao").replace(".", "").replace(",", ".")
        profissional.data_admissao = request.POST.get("dataAdmissao")
        profissional.horario_entrada = request.POST.get("horarioEntrada")
        profissional.intervalo_inicio = request.POST.get("intervaloInicio")
        profissional.intervalo_fim = request.POST.get("intervaloFim")
        profissional.horario_saida = request.POST.get("horarioSaida")
        profissional.save()

        messages.success(request, "Profissional atualizado com sucesso!")
        return redirect("listar_profissionais")

    return render(request, "ponto/cadastro.html", {
        "modo_gestor": True,
        "profissional": profissional,
        "edicao": True
    })


@login_required
def registrar_ponto(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        try:
            profissional = Profissional.objects.get(usuario=request.user)
            RegistroPonto.objects.create(profissional=profissional, tipo=tipo)
            messages.success(request, f"Ponto de {tipo} registrado com sucesso.")
        except Profissional.DoesNotExist:
            messages.error(request, "Profissional não encontrado.")
    return redirect("inicio")

@login_required
@user_passes_test(lambda u: u.is_staff)
def salvar_alteracoes_folha(request, profissional_id):
    """
    Processa o POST do template de edição em lote: atualiza cada RegistroPonto marcado.
    Após salvar, redireciona de volta para a mesma folha mantendo mes/ano.
    """
    profissional = get_object_or_404(Profissional, id=profissional_id)

    # Captura mês e ano atuais ou vindos na querystring
    mes_param = request.GET.get('mes')
    ano_param = request.GET.get('ano')
    try:
        mes = int(mes_param) if mes_param and mes_param.isdigit() else datetime.today().month
    except ValueError:
        mes = datetime.today().month
    try:
        ano = int(ano_param) if ano_param and ano_param.isdigit() else datetime.today().year
    except ValueError:
        ano = datetime.today().year

    registros = RegistroPonto.objects.filter(
        profissional=profissional,
        data__month=mes,
        data__year=ano
    )
    alterados = 0
    for ponto in registros:
        key_checkbox = f'editar_{ponto.id}'
        key_time = f'registro_{ponto.id}'
        if key_checkbox in request.POST:
            hora_str = request.POST.get(key_time)
            try:
                nova_hora = datetime.strptime(hora_str, '%H:%M').time()
                if ponto.hora != nova_hora:
                    ponto.hora = nova_hora
                    ponto.save(update_fields=['hora'])
                    alterados += 1
            except (ValueError, TypeError):
                messages.error(request, f"Horário inválido para {ponto.data} ({ponto.get_tipo_display()}).")

    if alterados:
        messages.success(request, f"{alterados} registro(s) atualizado(s) com sucesso.")
    else:
        messages.info(request, "Nenhuma alteração detectada.")

    # Reconstrói URL com querystring de mes e ano
    base_url = reverse('visualizar_folha', args=[profissional_id])
    return redirect(f'{base_url}?mes={mes}&ano={ano}')

@user_passes_test(lambda u: u.is_staff)
def listar_folhas(request):
    profissionais = Profissional.objects.select_related("usuario").all()
    return render(request, "ponto/folha_gestor.html", {
        "profissionais": profissionais
    })

@login_required
def visualizar_folha(request, profissional_id):
    # Busca o profissional
    profissional = get_object_or_404(Profissional, id=profissional_id)

    # Impede profissionais de verem folha de outro
    if not request.user.is_staff and profissional.usuario != request.user:
        messages.error(request, "Você só pode ver a sua própria folha.")
        return redirect("inicio")

    # Mês/ano (por GET ou atuais)
    mes = int(request.GET.get("mes", datetime.today().month))
    ano = int(request.GET.get("ano", datetime.today().year))

    registros = RegistroPonto.objects.filter(
        profissional=profissional,
        data__month=mes,
        data__year=ano
    ).order_by("data", "hora")

    # (manutenção do POST de edição para gestores…)

    # Calcula meses anterior/próximo …
    def anterior(m, a): return (12, a - 1) if m == 1 else (m - 1, a)
    def proximo(m, a):  return (1, a + 1) if m == 12 else (m + 1, a)
    mes_ant, ano_ant = anterior(mes, ano)
    mes_prox, ano_prox = proximo(mes, ano)

    # Escolhe o template conforme perfil
    if request.user.is_staff:
        template = "ponto/folha.html"
    else:
        template = "ponto/folha_profissional.html"

    return render(request, template, {
        "profissional": profissional,
        "registros": registros,
        "mes": mes,
        "ano": ano,
        "mes_anterior": {"mes": mes_ant, "ano": ano_ant},
        "mes_proximo":  {"mes": mes_prox, "ano": ano_prox},
        "pode_editar": request.user.is_staff,
        'tipos_padrao': ['entrada', 'pausa', 'retorno', 'saida'],
    })
                  
@login_required
def chat(request):
    # Apenas profissionais acessam esta página de chat
    if request.user.is_staff:
        return redirect('listar_profissionais')

    # Seleciona o primeiro gestor (usuário staff) para conversar
    gestor = Usuario.objects.filter(is_staff=True).first()

    return render(request, 'ponto/chat.html', {
        'gestor_id': gestor.id
    })