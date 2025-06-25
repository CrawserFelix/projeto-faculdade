from rest_framework import serializers
from .models import Mensagem

class MensagemSerializer(serializers.ModelSerializer):
    # remete o remetente como read-only (vem do request.user)
    remetente = serializers.ReadOnlyField(source='remetente.id')

    class Meta:
        model = Mensagem
        fields = ['id', 'remetente', 'destinatario', 'conteudo', 'criado_em', 'lido']
