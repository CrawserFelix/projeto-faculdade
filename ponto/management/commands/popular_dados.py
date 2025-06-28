from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ponto.models import Profissional, RegistroPonto
from django.utils import timezone
from datetime import date, datetime, timedelta, time
from decimal import Decimal
import calendar, random

class Command(BaseCommand):
    help = "Popula o banco de dados com profissionais e registros de ponto de 3 meses (dados de teste)."

    def handle(self, *args, **kwargs):
        User = get_user_model()
        gestor_user = User.objects.filter(is_staff=True).first()  # Usa o primeiro gestor disponível, se houver

        # Definir os últimos 3 meses (incluindo o mês atual)
        hoje = date.today()
        # Lista (ano, mes) para os três últimos meses
        meses = []
        for i in [2, 1, 0]:
            m = hoje.month - i
            y = hoje.year
            if m <= 0:
                m += 12
                y -= 1
            meses.append((y, m))

        num_profs = 5  # quantidade de profissionais a criar
        for i in range(1, num_profs + 1):
            # Dados do usuário/profissional
            cpf = str(80000000000 + i)  # Gera um CPF fictício de 11 dígitos
            nome = f"Funcionário {i}"
            email = f"funcionario{i}@exemplo.com"
            senha = "123456"
            # Cria usuário do sistema
            usuario = User.objects.create_user(cpf=cpf, password=senha,
                                               nome_completo=nome, email=email)
            # Gera data de nascimento aleatória entre 1970 e 2000
            ano_nasc = random.randint(1970, 2000)
            data_nasc = date(ano_nasc, 1, 1) + timedelta(days=random.randrange(365))
            # Define data de admissão no início do período (pelo menos 3 meses atrás)
            primeiro_mes = meses[0]  # mês/ano mais antigo da lista
            data_admissao = date(primeiro_mes[0], primeiro_mes[1], 1)
            # Define horário padrão (metade dos funcionários entra 8h, metade 9h, por exemplo)
            if random.random() < 0.5:
                hora_entrada = time(8, 0)
                ini_intervalo = time(12, 0)
                fim_intervalo = time(13, 0)
                hora_saida = time(17, 0)
            else:
                hora_entrada = time(9, 0)
                ini_intervalo = time(13, 0)
                fim_intervalo = time(14, 0)
                hora_saida = time(18, 0)
            # Cria Profissional
            prof = Profissional.objects.create(
                usuario=usuario,
                data_nascimento=data_nasc,
                telefone=None,
                remuneracao=Decimal(random.uniform(1200, 8000)).quantize(Decimal('0.00')),
                data_admissao=data_admissao,
                horario_entrada=hora_entrada,
                intervalo_inicio=ini_intervalo,
                intervalo_fim=fim_intervalo,
                horario_saida=hora_saida,
                gestor=gestor_user
            )

            # Função auxiliar para somar minutos a um horário (retorna datetime.time)
            def add_minutos(hora_base, minutos):
                total = hora_base.hour * 60 + hora_base.minute + minutos
                # Garante que horas extras não avancem dia (limita em 24h)
                if total < 0:
                    total = 0
                h = (total // 60) % 24
                m = total % 60
                return time(h, m)

            # Gera registros de ponto para os últimos 3 meses
            registros_novos = []
            for (ano, mes) in meses:
                # último dia do mês (ou até hoje, se mês atual)
                ultimo_dia = calendar.monthrange(ano, mes)[1]
                if ano == hoje.year and mes == hoje.month:
                    ultimo_dia = hoje.day
                for dia in range(1, ultimo_dia + 1):
                    data_dia = date(ano, mes, dia)
                    # Ignora finais de semana e datas antes da admissão
                    if data_dia.weekday() >= 5 or data_dia < data_admissao:
                        continue

                    # Horários base (copiados do horário padrão do profissional)
                    ent = hora_entrada
                    pausa = ini_intervalo
                    retorno = fim_intervalo
                    sai = hora_saida

                    # Decide aleatoriamente o cenário do dia
                    x = random.random()
                    if x < 0.10:       # atraso na entrada
                        atraso = random.randint(30, 90)      # 30-90 min de atraso
                        ent = add_minutos(ent, atraso)
                    elif x < 0.20:     # hora extra (sai mais tarde)
                        extra = random.randint(30, 120)     # 30-120 min extra
                        sai = add_minutos(sai, extra)
                    elif x < 0.25:     # saída antecipada
                        adiant = random.randint(30, 60)     # sai 30-60 min mais cedo
                        sai = add_minutos(sai, -adiant)
                    elif x < 0.30:     # sem intervalo (não registra pausa/retorno e sai 1h mais cedo)
                        pausa = None
                        retorno = None
                        sai = add_minutos(sai, -60)
                    else:
                        # dia normal (pode ter pequenas variações de minutos)
                        ent = add_minutos(ent, random.randint(-5, 5))
                        # Opcional: variar início/fim do almoço em até ±5 min
                        offset = random.randint(-5, 5)
                        pausa = add_minutos(pausa, offset)
                        retorno = add_minutos(retorno, offset)
                        sai = add_minutos(sai, random.randint(-5, 5))

                    # Para cenários com hora extra, saída antecipada ou sem intervalo, 
                    # ainda podemos adicionar pequena variação na entrada (±5 min)
                    if x < 0.30 and x >= 0.10:
                        ent = add_minutos(ent, random.randint(-5, 5))

                    # Monta os registros do dia (entrada sempre existe)
                    registros_novos.append(RegistroPonto(profissional=prof, data=data_dia, hora=ent, tipo='entrada'))
                    if pausa is not None:
                        registros_novos.append(RegistroPonto(profissional=prof, data=data_dia, hora=pausa, tipo='pausa'))
                    if retorno is not None:
                        registros_novos.append(RegistroPonto(profissional=prof, data=data_dia, hora=retorno, tipo='retorno'))
                    if sai is not None:
                        registros_novos.append(RegistroPonto(profissional=prof, data=data_dia, hora=sai, tipo='saida'))
            # Insere em lote os registros gerados para este profissional
            RegistroPonto.objects.bulk_create(registros_novos)

        self.stdout.write(self.style.SUCCESS(f"{num_profs} profissionais criados com pontos dos últimos 3 meses."))
