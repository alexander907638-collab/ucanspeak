from django.urls import path
from .views_jwt import LoginWithSessionView, RefreshWithSessionView

urlpatterns = [
    path('jwt/create/', LoginWithSessionView.as_view(), name='jwt_create'),
    path('jwt/refresh/', RefreshWithSessionView.as_view(), name='jwt_refresh'),
]
