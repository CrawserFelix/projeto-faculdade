from datetime import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra_fields):
        if not cpf:
            raise ValueError("O CPF é obrigatório")
        user = self.model(cpf=cpf, **extra_fields)
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
    usuario = models.OneToOneField('ponto.Usuario', on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)
    data_nascimento = models.DateField()
    remuneracao = models.DecimalField(max_digits=10, decimal_places=2)
    data_admissao = models.DateField()
    horario_entrada = models.TimeField()
    intervalo_inicio = models.TimeField()
    intervalo_fim = models.TimeField()
    horario_saida = models.TimeField()

    def __str__(self):
        return self.usuario.get_full_name()

def hora_truncada():
    now = timezone.localtime()
    return now.replace(second=0, microsecond=0).time()

class RegistroPonto(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)
    hora = models.TimeField(default=hora_truncada)
    tipo = models.CharField(max_length=10, choices=[
        ('entrada', 'Entrada'),
        ('pausa', 'Pausa'),
        ('retorno', 'Retorno'),
        ('saida', 'Saída')
    ])

class FolhaPonto(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    mes = models.IntegerField()
    ano = models.IntegerField()

    def __str__(self):
        return f"Folha de {self.profissional} - {self.mes}/{self.ano}"

class Mensagem(models.Model):
    remetente = models.ForeignKey('ponto.Usuario', on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey('ponto.Usuario', on_delete=models.CASCADE, related_name='mensagens_recebidas')
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    lido = models.BooleanField(default=False)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f"{self.remetente.nome_completo} para {self.destinatario.nome_completo} em {self.criado_em}"