from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from ..models import Mensagem
from ..serializers import MensagemSerializer

class ChatViewSet(viewsets.ModelViewSet):
    """
    GET  /api/chat/conversas/?gestor=<id>&usuario=<id>  → lista trocas entre esses dois.
    POST /api/chat/                                   → cria nova mensagem (remetente=request.user).
    """
    queryset = Mensagem.objects.all()
    serializer_class = MensagemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # assegura que o remetente seja sempre o usuário autenticado
        serializer.save(remetente=self.request.user)

    @action(detail=False, methods=['get'], url_path='conversas')
    def conversas(self, request):
        gestor_id    = request.query_params.get('gestor')
        usuario_id   = request.query_params.get('usuario') or request.query_params.get('user')
        if not gestor_id or not usuario_id:
            return Response([], status=400)

        msgs = Mensagem.objects.filter(
            Q(remetente_id__in=[gestor_id, usuario_id]) &
            Q(destinatario_id__in=[gestor_id, usuario_id])
        ).order_by('criado_em')
        serializer = self.get_serializer(msgs, many=True)
        return Response(serializer.data)
