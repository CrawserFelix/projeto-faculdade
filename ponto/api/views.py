# ponto/api/views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ..models import Mensagem, Usuario
from ..serializers import MensagemSerializer

class ChatViewSet(viewsets.GenericViewSet):
    """
    ViewSet para listar e enviar mensagens entre usuário e gestor.
    GET /api/chat/{conversa_id}/ → lista mensagens trocadas.
    POST /api/chat/ → envia nova mensagem com remetente definido pelo request.user.
    """
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        outro_id = self.kwargs.get('conversa_id')
        user = self.request.user
        return Mensagem.objects.filter(
            Q(remetente=user, destinatario__id=outro_id) |
            Q(remetente__id=outro_id, destinatario=user)
        ).order_by('criado_em')

    def list(self, request, conversa_id=None):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(remetente=request.user)
        return Response(serializer.data, status=201)
