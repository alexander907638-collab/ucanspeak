from rest_framework.routers import DefaultRouter
from .views import UserSessionViewSet

router = DefaultRouter()
router.register(r'sessions', UserSessionViewSet, basename='session')

urlpatterns = router.urls
