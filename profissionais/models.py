from django.db import models
from django.utils import timezone
from usuarios.models import Usuario

class Ponto(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('pausa', 'Pausa'),
        ('retorno', 'Retorno'),
        ('saida', 'Saída'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data = models.DateField(default=timezone.localdate)
    hora = models.TimeField(default=timezone.localtime)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.usuario.nome_completo} - {self.tipo} - {self.data} {self.hora}"

class Profissional(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.PROTECT, verbose_name="Usuário")

    cargo = models.CharField(max_length=50, verbose_name="Cargo")
    gestor = models.CharField(max_length=100, verbose_name="Nome do Gestor")
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    remuneracao = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Remuneração")

    telefone = models.CharField(max_length=11, verbose_name="Telefone")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        db_table = "profissional"

    def __str__(self):
        return self.usuario.nome_completo
