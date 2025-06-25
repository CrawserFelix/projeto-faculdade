from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from calendar import month_name, monthrange
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.db.models import Q

from .models import Profissional, RegistroPonto, Mensagem

User = get_user_model()


def index(request):
    return render(request, "ponto/inicio.html")


def login_usuario(request):
    if request.method == "POST":
        cpf = request.POST.get("username")
        senha = request.POST.get("password")
        usuario = authenticate(request, cpf=cpf, password=senha)
        if usuario:
            login(request, usuario)
            return redirect("inicio")
        messages.error(request, "CPF ou senha inválidos.")
    return render(request, "ponto/login.html")


def logout_usuario(request):
    logout(request)
    return redirect("login")


User = get_user_model()

@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastrar_profissional(request):
    """
    Permite ao gestor criar um novo Profissional.
    Cria primeiro o Usuario (com CPF, nome, email e senha),
    depois cria o Profissional ligando-o ao Usuario e ao gestor.
    """
    if request.method == "POST":
        # --- 1) Campos de usuário ---
        cpf_raw   = request.POST.get("cpf", "")
        cpf       = cpf_raw.replace(".", "").replace("-", "")
        nome      = request.POST.get("nomeCompleto")
        email     = request.POST.get("email")
        senha     = request.POST.get("senha")

        if User.objects.filter(cpf=cpf).exists():
            messages.error(request, "Já existe um usuário com esse CPF.")
            return redirect("cadastrar_profissional")

        usuario = User.objects.create_user(
            cpf=cpf,
            nome_completo=nome,
            email=email,
            password=senha
        )

        # --- 2) Campos de Profissional ---
        data_nascimento = request.POST.get("dataNascimento")
        telefone        = request.POST.get("telefone") or None
        remuneracao_raw = request.POST.get("remuneracao", "0")
        remuneracao     = remuneracao_raw.replace(".", "").replace(",", ".")
        data_admissao   = request.POST.get("dataAdmissao")
        horario_entrada = request.POST.get("horarioEntrada")
        intervalo_inicio= request.POST.get("intervaloInicio")
        intervalo_fim   = request.POST.get("intervaloFim")
        horario_saida   = request.POST.get("horarioSaida")

        # --- 3) Seleção do gestor ---
        gestor_id = request.POST.get("gestor")
        gestor_user = None
        if gestor_id:
            gestor_user = User.objects.filter(id=gestor_id, is_staff=True).first()
            if not gestor_user:
                messages.error(request, "Gestor selecionado inválido.")
                return redirect("cadastrar_profissional")

        # --- 4) Cria o Profissional ---
        Profissional.objects.create(
            usuario=usuario,
            data_nascimento=data_nascimento,
            telefone=telefone,
            remuneracao=remuneracao,
            data_admissao=data_admissao,
            horario_entrada=horario_entrada,
            intervalo_inicio=intervalo_inicio,
            intervalo_fim=intervalo_fim,
            horario_saida=horario_saida,
            gestor=gestor_user
        )

        messages.success(request, "Profissional cadastrado com sucesso.")
        return redirect("listar_profissionais")

    # --- GET: renderiza o formulário com dropdown de gestores ---
    gestores = User.objects.filter(is_staff=True).order_by("nome_completo")
    return render(request, "ponto/cadastro.html", {
        "modo_gestor": True,
        "gestores": gestores,
    })


@login_required
def cadastro_profissional_usuario(request):
    """Profissional comum vê seus dados."""
    prof = Profissional.objects.filter(usuario=request.user).first()
    return render(request, "ponto/cadastro.html", {
        "modo_gestor": False,
        "profissional": prof
    })


@login_required
def listar_profissionais(request):
    profissionais = Profissional.objects.select_related('usuario').all()
    return render(request, "ponto/lista.html", {"profissionais": profissionais})


@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_profissional(request, profissional_id):
    prof = get_object_or_404(Profissional, id=profissional_id)
    if request.method == 'POST':
        # atualiza user
        u = prof.usuario
        u.nome_completo = request.POST.get('nomeCompleto')
        u.email = request.POST.get('email')
        u.save()
        # atualiza prof
        prof.telefone = request.POST.get('telefone')
        prof.data_nascimento = request.POST.get('dataNascimento')
        prof.remuneracao = request.POST.get('remuneracao').replace('.','').replace(',','.')
        prof.data_admissao = request.POST.get('dataAdmissao')
        prof.horario_entrada = request.POST.get('horarioEntrada')
        prof.intervalo_inicio = request.POST.get('intervaloInicio')
        prof.intervalo_fim = request.POST.get('intervaloFim')
        prof.horario_saida = request.POST.get('horarioSaida')
        # gestor
        gestor_id = request.POST.get('gestor')
        gestor_user = User.objects.filter(id=gestor_id, is_staff=True).first() if gestor_id else None
        prof.gestor = gestor_user
        prof.save()
        messages.success(request, 'Profissional atualizado com sucesso!')
        return redirect('listar_profissionais')
    gestores = User.objects.filter(is_staff=True)
    return render(request, 'ponto/cadastro.html', {
        'modo_gestor': True,
        'profissional': prof,
        'edicao': True,
        'gestores': gestores
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def excluir_profissional(request, profissional_id):
    prof = get_object_or_404(Profissional, id=profissional_id)
    if request.method == 'POST':
        prof.usuario.delete()
        prof.delete()
        messages.success(request, 'Profissional excluído com sucesso!')
        return redirect('listar_profissionais')
    return render(request, 'ponto/confirmar_exclusao.html', {'profissional': prof})


@login_required
def registrar_ponto(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        prof = Profissional.objects.filter(usuario=request.user).first()
        if prof:
            RegistroPonto.objects.create(profissional=prof, tipo=tipo)
            messages.success(request, f'Ponto de {tipo} registrado com sucesso.')
        else:
            messages.error(request, 'Profissional não encontrado.')
    return redirect('inicio')

@login_required
@user_passes_test(lambda u: u.is_staff)
def salvar_alteracoes_folha(request, profissional_id):
    """
    Processa edição em lote da folha de ponto para um profissional:
      - Atualiza todos os registros marcados (checkbox `editar_<id>`)
      - Mantém mês/ano na querystring ao redirecionar de volta
    """
    prof = get_object_or_404(Profissional, id=profissional_id)

    # lê mês e ano da querystring ou usa os atuais
    mes_str = request.GET.get('mes')
    ano_str = request.GET.get('ano')
    try:
        mes = int(mes_str) if mes_str and mes_str.isdigit() else datetime.today().month
    except:
        mes = datetime.today().month
    try:
        ano = int(ano_str) if ano_str and ano_str.isdigit() else datetime.today().year
    except:
        ano = datetime.today().year

    registros = RegistroPonto.objects.filter(
        profissional=prof,
        data__month=mes,
        data__year=ano
    )
    alterados = 0
    for ponto in registros:
        chk = f'editar_{ponto.id}'
        time_field = f'registro_{ponto.id}'
        if chk in request.POST:
            hora_str = request.POST.get(time_field)
            try:
                nova_hora = datetime.strptime(hora_str, '%H:%M').time()
                if ponto.hora != nova_hora:
                    ponto.hora = nova_hora
                    ponto.save(update_fields=['hora'])
                    alterados += 1
            except:
                messages.error(request, f"Horário inválido em {ponto.data}")

    if alterados:
        messages.success(request, f"{alterados} registro(s) atualizado(s) com sucesso.")
    else:
        messages.info(request, "Nenhuma alteração detectada.")

    # reconstrói URL mantendo mês e ano
    url = reverse('visualizar_folha', args=[profissional_id])
    return redirect(f"{url}?mes={mes}&ano={ano}")

@login_required
@user_passes_test(lambda u: u.is_staff)
def listar_folhas(request):
    profissionais = Profissional.objects.select_related('usuario').all()
    return render(request, 'ponto/folha_gestor.html', {'profissionais': profissionais})


@login_required
def visualizar_folha(request, profissional_id):
    prof = get_object_or_404(Profissional, id=profissional_id)
    if not request.user.is_staff and prof.usuario != request.user:
        messages.error(request, 'Você só pode ver a sua própria folha.')
        return redirect('inicio')
    # mes/ano
    mes = int(request.GET.get('mes', datetime.today().month))
    ano = int(request.GET.get('ano', datetime.today().year))
    registros = RegistroPonto.objects.filter(
        profissional=prof,
        data__month=mes,
        data__year=ano
    ).order_by('data', 'hora')
    # navegar
    def adj(m,a,delta): return (12, a-1) if delta<0 and m==1 else (1, a+1) if delta>0 and m==12 else (m+delta,a)
    mes_ant, ano_ant = adj(mes,ano,-1)
    mes_prox, ano_prox = adj(mes,ano,1)
    # template
    tpl = 'ponto/folha.html' if request.user.is_staff else 'ponto/folha_profissional.html'
    return render(request, tpl, {
        'profissional': prof,
        'registros': registros,
        'mes': mes, 'ano': ano,
        'mes_anterior': {'mes': mes_ant,'ano': ano_ant},
        'mes_proximo': {'mes': mes_prox,'ano': ano_prox},
        'pode_editar': request.user.is_staff,
        'tipos_padrao': ['entrada','pausa','retorno','saida'],
    })


@login_required
def chat_profissional(request):
    prof = get_object_or_404(Profissional, usuario=request.user)
    gestor_user = prof.gestor  
    gestor_id = gestor_user.id if gestor_user else None

    return render(request, 'ponto/chat_profissional.html', {
        'userId':   request.user.id,
        'gestorId': gestor_id,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def chat_gestor(request, profissional_id=None):
    user = request.user
    # equipe: todos que apontam este user como gestor
    equipe = Profissional.objects.filter(gestor=user).select_related('usuario')
    # unread counts
    unread_items = []
    for p in equipe:
        count = Mensagem.objects.filter(
            remetente=p.usuario,
            destinatario=user,
            lido=False
        ).count()
        unread_items.append((p, count))
    conversa = []
    ativo = None
    if profissional_id:
        ativo = get_object_or_404(Profissional, id=profissional_id, gestor=user)
        conversa = Mensagem.objects.filter(
            Q(remetente=ativo.usuario, destinatario=user) |
            Q(remetente=user, destinatario=ativo.usuario)
        ).order_by('criado_em')
        Mensagem.objects.filter(
            remetente=ativo.usuario,
            destinatario=user,
            lido=False
        ).update(lido=True)
    return render(request, 'ponto/chat_gestor.html', {
        'profissionais': equipe,
        'unread_items': unread_items,
        'conversa': conversa,
        'ativo': ativo,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    # 1) Meses
    meses = [
        {'value': i, 'display': month_name[i]}
        for i in range(1, 13)
    ]
    # 2) Mês e ano correntes ou vindos da querystring
    hoje = datetime.today()
    mes_get = request.GET.get('mes')
    ano_get = request.GET.get('ano')
    try:
        mes_atual = int(mes_get) if mes_get and mes_get.isdigit() else hoje.month
    except ValueError:
        mes_atual = hoje.month
    try:
        ano_atual = int(ano_get) if ano_get and ano_get.isdigit() else hoje.year
    except ValueError:
        ano_atual = hoje.year

    # 3) Anos disponíveis nos registros (ou apenas o ano atual)
    anos_reg = {r.data.year for r in RegistroPonto.objects.all()}
    anos = sorted(anos_reg) if anos_reg else [hoje.year]

    # 4) Profissionais da sua equipe
    # supondo que gestor → Profissional.usuario = request.user
    gestor_prof = Profissional.objects.filter(usuario=request.user).first()
    if gestor_prof:
        profissionais = Profissional.objects.filter(gestor=request.user).select_related('usuario')
    else:
        profissionais = Profissional.objects.none()

    return render(request, "ponto/inicio.html", {
        "meses": meses,
        "mes_atual": mes_atual,
        "anos": anos,
        "ano_atual": ano_atual,
        "profissionais": profissionais,
    })

@login_required
def dashboard_data(request):
    # 1) pega o profissional
    prof_id = request.GET.get('profissional')
    if prof_id and prof_id.isdigit():
        profissional = get_object_or_404(Profissional, id=int(prof_id))
    else:
        # se não veio ou inválido, e for usuário comum, usa o próprio
        if request.user.is_staff:
            return JsonResponse({'error': 'Parâmetro profissional faltando ou inválido.'}, status=400)
        profissional = get_object_or_404(Profissional, usuario=request.user)

    # 2) mês e ano
    hoje = datetime.today()
    mes_param = request.GET.get('mes', '')
    ano_param = request.GET.get('ano', '')

    if mes_param.isdigit():
        mes = int(mes_param)
    else:
        mes = hoje.month

    if ano_param.isdigit():
        ano = int(ano_param)
    else:
        ano = hoje.year

    # 3) busca registros do mês/ano
    registros = RegistroPonto.objects.filter(
        profissional=profissional,
        data__year=ano,
        data__month=mes
    )

    # 4) monta dados do dashboard (exemplo de saída; adapte ao que precisar)
    #   vamos agrupar por dia e calcular atrasos, horas trabalhadas, etc.
    from collections import defaultdict
    dados = defaultdict(lambda: {'entrada': None, 'pausa': None, 'retorno': None, 'saida': None})

    for reg in registros:
        dia = reg.data.day
        dados[dia][reg.tipo] = reg.hora.strftime('%H:%M')

    # 5) serializa em lista ordenada
    resultado = []
    for dia in sorted(dados):
        resultado.append({
            'dia': dia,
            **dados[dia]
        })

    return JsonResponse({
        'profissional': profissional.usuario.nome_completo,
        'mes': mes,
        'ano': ano,
        'registros': resultado
    })