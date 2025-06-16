from rest_framework import serializers
from .models import Mensagem

class MensagemSerializer(serializers.ModelSerializer):
    remetente = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Mensagem
        fields = ['id', 'remetente', 'destinatario', 'conteudo', 'criado_em', 'lido']
        read_only_fields = ['id', 'criado_em', 'lido']