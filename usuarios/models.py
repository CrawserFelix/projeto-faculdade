from typing import Any
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None):
        Usuario = self.model(
            email=self.normalize_email(email)
        )

        Usuario.is_active = True
        Usuario.is_staff = False
        Usuario.is_superuser = False

        if password:
            Usuario.set_password(password)
        
        Usuario.save()

        return Usuario
    
    def create_superuser(self, email, password):
        Usuario = self.create_user(
            email=self.normalize_email(email),
            password=password
        )

        Usuario.is_active = True
        Usuario.is_staff = True
        Usuario.is_superuser = True

        Usuario.set_password(password)

        Usuario.save()

        return Usuario

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="E-mail do usuário",
        max_length=255,
        unique=True
        )
    
    is_active = models.BooleanField(
        verbose_name="Usuário está ativo",
        default=True
        )
    
    is_staff = models.BooleanField(
        verbose_name="Usuário é da equipe de desenvolvimento",
        default=False
        )
    
    is_superuser = models.BooleanField(
        verbose_name="Usuário é um superusuario",
        default=False
    )

    USERNAME_FIELD = "email"

    objects = UsuarioManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = "usuario"

    def __str__(self):
        return self.email
    
    