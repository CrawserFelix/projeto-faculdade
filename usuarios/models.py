from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
