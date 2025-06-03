from django.shortcuts import render, redirect
from .models import Ponto, Profissional
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from datetime import datetime, timedelta, date, time
from calendar import monthrange
from django.utils.timezone import make_aware


@login_required
def folha_de_ponto(request):
    # Pega mês e ano da URL, ou usa o mês atual
    mes = int(request.GET.get('mes', datetime.now().month))
    ano = int(request.GET.get('ano', datetime.now().year))

    # Dias do mês atual
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, monthrange(ano, mes)[1])

    # Pontos do usuário no mês
    pontos_raw = Ponto.objects.filter(
        usuario=request.user,
        data__range=(primeiro_dia, ultimo_dia)
    ).order_by("data", "hora")

    # Agrupar por data
    pontos_agrupados = defaultdict(lambda: {"entrada": "", "pausa": "", "retorno": "", "saida": ""})

    for ponto in pontos_raw:
        pontos_agrupados[ponto.data][ponto.tipo] = ponto.hora.strftime("%H:%M")

    # Criar lista de todos os dias do mês
    dias_do_mes = []
    for dia in range(1, monthrange(ano, mes)[1] + 1):
        data = date(ano, mes, dia)
        tipos = pontos_agrupados.get(data, {"entrada": "-", "pausa": "-", "retorno": "-", "saida": "-"})
        total_horas = calcular_horas_trabalhadas(tipos)
        tipos["total"] = str(total_horas) if total_horas else "-"
        dias_do_mes.append((data, tipos))


    # Controle de navegação
    mes_anterior = (mes - 1) or 12
    ano_anterior = ano if mes > 1 else ano - 1
    mes_proximo = (mes % 12) + 1
    ano_proximo = ano if mes < 12 else ano + 1

    return render(request, "folhaDePonto.html", {
        "dias": dias_do_mes,
        "mes": mes,
        "ano": ano,
        "mes_anterior": mes_anterior,
        "ano_anterior": ano_anterior,
        "mes_proximo": mes_proximo,
        "ano_proximo": ano_proximo,
    })

def calcular_horas_trabalhadas(tipos):
    """Recebe um dicionário com os tipos de ponto e retorna timedelta com o tempo trabalhado."""
    def str_para_hora(s):
        try:
            return datetime.strptime(s, "%H:%M").time()
        except:
            return None

    entrada = str_para_hora(tipos.get("entrada"))
    pausa = str_para_hora(tipos.get("pausa"))
    retorno = str_para_hora(tipos.get("retorno"))
    saida = str_para_hora(tipos.get("saida"))

    if entrada and saida:
        # Se houver pausa e retorno
        if pausa and retorno:
            manha = datetime.combine(datetime.today(), pausa) - datetime.combine(datetime.today(), entrada)
            tarde = datetime.combine(datetime.today(), saida) - datetime.combine(datetime.today(), retorno)
            return manha + tarde
        else:
            # Sem pausa, calcula direto
            return datetime.combine(datetime.today(), saida) - datetime.combine(datetime.today(), entrada)
    return None

@login_required
def registrar_ponto(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        Ponto.objects.create(
            usuario=request.user,
            tipo=tipo,
            data=timezone.localdate(),
            hora=timezone.localtime()
        )
        messages.success(request, f"{tipo.capitalize()} registrada com sucesso!")
        return redirect("registrar_ponto")

    return render(request, "registrarPonto.html")