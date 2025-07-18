from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CryptoCurrencyViewSet

router = DefaultRouter()
router.register(r'cryptos', CryptoCurrencyViewSet, basename='crypto')

urlpatterns = [
    path('', include(router.urls)),
]