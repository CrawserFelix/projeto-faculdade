from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()
# rota padrão POST /api/chat/ e GET /api/chat/{conversa_id}/
router.register(r'chat/(?P<conversa_id>[^/.]+)', ChatViewSet, basename='chat')

urlpatterns = router.urls