from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet

router = DefaultRouter()
# Registra as rotas:
# GET  /api/chat/conversas/  → ChatViewSet.conversas
# POST /api/chat/            → ChatViewSet.create
# (não expõe os detalhes individuais)
router.register(r'chat/(?P<conversa_id>[^/.]+)', ChatViewSet, basename='chat')

urlpatterns = router.urls
urlpatterns += [
    path('chat/', ChatViewSet.as_view({'post': 'create'}), name='chat_api'),
]
