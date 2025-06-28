from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404
from datetime import date, datetime



def hora_truncada():
    """Retorna hora atual sem segundos nem microssegundos"""
    now = timezone.localtime()
    return now.replace(second=0, microsecond=0).time()

class UsuarioManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra_fields):
        if not cpf:
            raise ValueError("O CPF é obrigatório")
        cpf_clean = cpf.replace(".", "").replace("-", "")
        user = self.model(cpf=cpf_clean, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not password:
            raise ValueError("Superusuário precisa de uma senha")
        return self.create_user(cpf, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField(max_length=11, unique=True, verbose_name="CPF")
    nome_completo = models.CharField(max_length=100, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="E-mail")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "cpf"
    REQUIRED_FIELDS = ['nome_completo', 'email']

    objects = UsuarioManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = "usuario"

    def __str__(self):
        return f"{self.nome_completo} ({self.cpf})"

    def get_full_name(self):
        return self.nome_completo

class Profissional(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuário"
    )
    #cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    telefone = models.CharField(max_length=20, blank=True, null=True)
    remuneracao = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    horario_entrada = models.TimeField(verbose_name="Horário de Entrada")
    intervalo_inicio = models.TimeField(verbose_name="Início do Intervalo")
    intervalo_fim = models.TimeField(verbose_name="Fim do Intervalo")
    horario_saida = models.TimeField(verbose_name="Horário de Saída")

    gestor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subordinados",
        verbose_name="Gestor"
    )

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ['usuario__nome_completo']

    def __str__(self):
        return f"{self.usuario.nome_completo} ({self.usuario.cpf})"

class RegistroPonto(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    data = models.DateField(default=date.today)
    hora = models.TimeField(default=hora_truncada)
    tipo = models.CharField(max_length=10, choices=[
        ('entrada', 'Entrada'),
        ('pausa', 'Pausa'),
        ('retorno', 'Retorno'),
        ('saida', 'Saída')
    ])

    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        ordering = ['-data', '-hora']

    def __str__(self):
        return f"{self.profissional.usuario.nome_completo} - {self.tipo} às {self.hora} em {self.data}"

class FolhaPonto(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    mes = models.IntegerField()
    ano = models.IntegerField()

    class Meta:
        unique_together = ('profissional', 'mes', 'ano')
        verbose_name = "Folha de Ponto"
        verbose_name_plural = "Folhas de Ponto"

    def __str__(self):
        return f"Folha de {self.profissional.usuario.nome_completo} - {self.mes}/{self.ano}"

from django.conf import settings
from django.db import models

class Mensagem(models.Model):
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensagens_enviadas',
        db_index=True,
        verbose_name="Remetente"
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensagens_recebidas',
        db_index=True,
        verbose_name="Destinatário"
    )
    conteudo = models.TextField(verbose_name="Conteúdo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    lido = models.BooleanField(default=False, verbose_name="Lida?")

    class Meta:
        ordering = ['criado_em']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        indexes = [
            models.Index(fields=['remetente', 'destinatario', 'criado_em']),
        ]

    def __str__(self):
        # Exibe algo como "José → Maria (2025-06-17 08:46)"
        timestamp = self.criado_em.strftime("%Y-%m-%d %H:%M")
        return f"{self.remetente.get_full_name()} → {self.destinatario.get_full_name()} ({timestamp})"

    def marcar_como_lida(self):
        if not self.lido:
            self.lido = True
            self.save(update_fields=['lido'])
