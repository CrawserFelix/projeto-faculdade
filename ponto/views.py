from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date
from calendar import month_name, monthrange
from django.views.decorators.http import require_GET
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.db.models import Q

from .models import Profissional, RegistroPonto, Mensagem

User = get_user_model()


def index(request):
    if request.user.is_staff:
        return dashboard(request)
    else:
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
@user_passes_test(lambda u: u.is_staff)
def listar_profissionais(request):
    # Inicia o queryset buscando todos os profissionais com o usuário relacionado
    profissionais = Profissional.objects.select_related('usuario').all()

    # Filtra por nome, se veio no GET
    nome = request.GET.get('nome')
    if nome:
        profissionais = profissionais.filter(
            usuario__nome_completo__icontains=nome
        )

    # Filtra por CPF (removendo pontos e traços), se veio no GET
    cpf = request.GET.get('cpf')
    if cpf:
        cpf_clean = cpf.replace('.', '').replace('-', '')
        profissionais = profissionais.filter(
            usuario__cpf__icontains=cpf_clean
        )

    # Renderiza passando o queryset filtrado
    return render(request, "ponto/lista.html", {
        "profissionais": profissionais
    })



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

def obter_datas_do_mes(ano, mes):
    """
    Retorna lista de objetos date para cada dia do mês especificado.
    """
    qtd_dias = monthrange(ano, mes)[1]  # obtém quantidade de dias no mês
    return [date(ano, mes, dia) for dia in range(1, qtd_dias + 1)]

# Exemplo de uso na view:
datas = obter_datas_do_mes(2025, 6)

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
    created_count = 0
    
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
    # Processa novos registros adicionados via campos "novo_*"
    for key, val in request.POST.items():
        if key.startswith('novo_') and val:
            # Formato da chave: "novo_<tipo>_<YYYY-MM-DD>"
            try:
                _, tipo, data_str = key.split('_', 2)
            except ValueError:
                continue
            try:
                data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
                hora_obj = datetime.strptime(val, "%H:%M").time()
            except ValueError:
                messages.error(request, f"Formato inválido para novo registro em {data_str}.")
                continue
            # Evita duplicar registro se já existir mesmo tipo naquele dia
            if RegistroPonto.objects.filter(profissional=prof, data=data_obj, tipo=tipo).exists():
                continue
            RegistroPonto.objects.create(profissional=prof, data=data_obj, hora=hora_obj, tipo=tipo)
            created_count += 1
    if alterados and created_count:
        messages.success(request, f"{alterados} registro(s) atualizado(s) e {created_count} registro(s) criado(s) com sucesso.")
    elif alterados:
        messages.success(request, f"{alterados} registro(s) atualizado(s) com sucesso.")
    elif created_count:
        messages.success(request, f"{created_count} registro(s) criado(s) com sucesso.")
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
    # Determina mês/ano a exibir
    mes = int(request.GET.get('mes', datetime.today().month))
    ano = int(request.GET.get('ano', datetime.today().year))
    registros = RegistroPonto.objects.filter(
        profissional=prof,
        data__month=mes,
        data__year=ano
    ).order_by('data', 'hora')
    # Cálculo para navegação entre meses
    def adj(m,a,delta): return (12, a-1) if delta<0 and m==1 else (1, a+1) if delta>0 and m==12 else (m+delta,a)
    mes_ant, ano_ant = adj(mes,ano,-1)
    mes_prox, ano_prox = adj(mes,ano,1)
    # Prepara lista de dias do mês com seus registros (None se não houve ponto naquele dia)
    from collections import defaultdict
    regs_by_date = defaultdict(list)
    for r in registros:
        regs_by_date[r.data].append(r)
    dias = []
    num_dias = monthrange(ano, mes)[1]
    for dia in range(1, num_dias+1):
        data_atual = date(ano, mes, dia)
        entrada = pausa = retorno = saida = None
        for r in regs_by_date.get(data_atual, []):
            if r.tipo == 'entrada':
                entrada = r
            elif r.tipo == 'pausa':
                pausa = r
            elif r.tipo == 'retorno':
                retorno = r
            elif r.tipo == 'saida':
                saida = r
        dias.append({
            'data': data_atual,
            'entrada': entrada,
            'pausa': pausa,
            'retorno': retorno,
            'saida': saida
        })
    # Renderiza o template unificado da folha de ponto
    return render(request, 'ponto/folha.html', {
        'profissional': prof,
        'dias': dias,
        'mes': mes, 'ano': ano,
        'mes_anterior': {'mes': mes_ant, 'ano': ano_ant},
        'mes_proximo': {'mes': mes_prox, 'ano': ano_prox},
        'pode_editar': request.user.is_staff
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
    # 1) Meses (1–12) com nomes em português
    meses = [{'value': i, 'display': month_name[i]} for i in range(1, 13)]

    # 2) Mês e ano correntes ou vindos da querystring
    hoje = datetime.today()
    mes_atual = request.GET.get('mes')
    ano_atual = request.GET.get('ano')
    try:
        mes_atual = int(mes_atual) if mes_atual and mes_atual.isdigit() else hoje.month
    except ValueError:
        mes_atual = hoje.month
    try:
        ano_atual = int(ano_atual) if ano_atual and ano_atual.isdigit() else hoje.year
    except ValueError:
        ano_atual = hoje.year

    # 3) Anos disponíveis nos registros (ou apenas o ano atual)
    anos_reg = {r.data.year for r in RegistroPonto.objects.all()}
    anos = sorted(anos_reg) if anos_reg else [hoje.year]

    # 4) Profissionais subordinados ao gestor logado
    profissionais = (
        Profissional.objects
        .filter(gestor=request.user)
        .select_related('usuario')
    )

    return render(request, "ponto/inicio.html", {
        "meses": meses,
        "mes_atual": mes_atual,
        "anos": anos,
        "ano_atual": ano_atual,
        "profissionais": profissionais,
    })

@login_required
@require_GET
def dashboard_data(request):
    user = request.user
    mes = request.GET.get('mes')
    ano = request.GET.get('ano')
    prof_id = request.GET.get('profissional')

    # valida mês e ano
    try:
        mes = int(mes) if mes and mes.isdigit() else datetime.today().month
        ano = int(ano) if ano and ano.isdigit() else datetime.today().year
    except ValueError:
        return HttpResponseBadRequest("Parâmetros de mês ou ano inválidos.")

    # determina o profissional alvo
    if user.is_staff:
        if not prof_id or not prof_id.isdigit():
            return HttpResponseBadRequest("Gestor deve especificar um profissional.")
        try:
            profissional = Profissional.objects.get(pk=int(prof_id), gestor=user)
        except Profissional.DoesNotExist:
            return HttpResponseBadRequest("Profissional não encontrado ou sem permissão.")
    else:
        try:
            profissional = Profissional.objects.get(usuario=user)
        except Profissional.DoesNotExist:
            return HttpResponseBadRequest("Profissional não cadastrado para este usuário.")

    # monta o objeto 'esperado' com os horários padrão
    esperado = {
        "entrada": profissional.horario_entrada.strftime("%H:%M") if profissional.horario_entrada else None,
        "inicio_intervalo": profissional.intervalo_inicio.strftime("%H:%M") if profissional.intervalo_inicio else None,
        "fim_intervalo": profissional.intervalo_fim.strftime("%H:%M") if profissional.intervalo_fim else None,
        "saida": profissional.horario_saida.strftime("%H:%M") if profissional.horario_saida else None,
    }

    # busca os registros do mês/ano
    registros_raw = RegistroPonto.objects.filter(
        profissional=profissional,
        data__year=ano,
        data__month=mes
    ).order_by('data', 'hora')

    # Monta dicionário de dias com horários registrados (strings HH:MM)
    dias = {}
    for reg in registros_raw:
        d = reg.data.day
        if d not in dias:
            dias[d] = {"dia": d, "entrada": None, "pausa": None, "retorno": None, "saida": None}
        dias[d][reg.tipo] = reg.hora.strftime("%H:%M")
    # Garante que todos os dias do mês estejam presentes no resultado
    ultimo_dia = monthrange(ano, mes)[1]
    for d in range(1, ultimo_dia+1):
        if d not in dias:
            dias[d] = {"dia": d, "entrada": None, "pausa": None, "retorno": None, "saida": None}
    # Converte dicionário para lista ordenada por dia
    realizado = [dias[d] for d in sorted(dias.keys())]
    # Calcula métricas: atrasos, faltas e horas extras
    atrasos = 0
    faltas = 0
    total_extras_min = 0
    # Horários esperados (datetime.time) para comparação
    entrada_esperada = datetime.strptime(esperado["entrada"], "%H:%M").time() if esperado["entrada"] else None
    saida_esperada = datetime.strptime(esperado["saida"], "%H:%M").time() if esperado["saida"] else None
    for entry in realizado:
        # Verifica falta (dia útil sem nenhum registro)
        if (entry["entrada"] is None and entry["pausa"] is None and entry["retorno"] is None and entry["saida"] is None):
            # Determina o dia da semana (0=Segunda,...,6=Domingo)
            try:
                data_atual = date(ano, mes, entry["dia"])
            except Exception:
                data_atual = None
            if data_atual and data_atual.weekday() < 5:  # só conta faltas em dias úteis (segunda a sexta)
                faltas += 1
        else:
            # Atraso: Entrada registrada após horário esperado
            if entry["entrada"] and entrada_esperada:
                try:
                    entrada_real = datetime.strptime(entry["entrada"], "%H:%M").time()
                except ValueError:
                    entrada_real = None
                if entrada_real and entrada_real > entrada_esperada:
                    atrasos += 1
            # Horas extras: Saída registrada após horário de saída esperado
            if entry["saida"] and saida_esperada:
                try:
                    saida_real = datetime.strptime(entry["saida"], "%H:%M").time()
                except ValueError:
                    saida_real = None
                if saida_real and saida_real > saida_esperada:
                    # Calcula diferença em minutos entre saída real e esperada
                    extra_min = (saida_real.hour * 60 + saida_real.minute) - (saida_esperada.hour * 60 + saida_esperada.minute)
                    if extra_min > 0:
                        total_extras_min += extra_min
    # Formata horas extras em horas e minutos (ex: "2h 30min")
    if total_extras_min > 0:
        horas = total_extras_min // 60
        mins = total_extras_min % 60
        if horas > 0 and mins > 0:
            horas_extras_str = f"{horas}h {mins}min"
        elif horas > 0:
            horas_extras_str = f"{horas}h"
        else:
            horas_extras_str = f"{mins}min"
    else:
        horas_extras_str = "0"

    return JsonResponse({
        "profissional": profissional.usuario.nome_completo,
        "mes": mes,
        "ano": ano,
        "esperado": esperado,
        "realizado": realizado,
        "atrasos": atrasos,
        "faltas": faltas,
        "horas_extras": horas_extras_str
    })