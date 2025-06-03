from django.contrib.auth.backends import ModelBackend
from usuarios.models import Usuario

class AutenticadorCPFBackend(ModelBackend):
    def authenticate(self, request, cpf=None, password=None, **kwargs):
        try:
            usuario = Usuario.objects.get(cpf=cpf)
            if usuario.check_password(password):
                return usuario
        except Usuario.DoesNotExist:
            return None
