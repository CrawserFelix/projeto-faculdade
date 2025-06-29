from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from ..models import Mensagem
from ..serializers import MensagemSerializer

class ChatViewSet(viewsets.ModelViewSet):
    """
    POST /api/chat/           → cria nova mensagem (remetente=request.user)
    GET  /api/chat/?gestor=&usuario=  → lista trocas entre esses dois usuários
    """
    queryset = Mensagem.objects.none()
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        gestor_id  = self.request.query_params.get('gestor')
        usuario_id = (self.request.query_params.get('usuario') or
                      self.request.query_params.get('user'))
        if gestor_id and usuario_id:
            return Mensagem.objects.filter(
                Q(remetente_id__in=[gestor_id, usuario_id]) &
                Q(destinatario_id__in=[gestor_id, usuario_id])
            ).order_by('criado_em')
        return Mensagem.objects.none()

    def list(self, request, *args, **kwargs):
        gestor_id  = request.query_params.get('gestor')
        usuario_id = (request.query_params.get('usuario') or
                      request.query_params.get('user'))
        # Se faltarem params, erro 400:
        if not gestor_id or not usuario_id:
            return Response(
                {'detail': 'Parâmetros gestor e usuário são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Caso sem mensagens, devolve array vazio:
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # garante que remetente é sempre o user logado
        serializer.save(remetente=self.request.user)
