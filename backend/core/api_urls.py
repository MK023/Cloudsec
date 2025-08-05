from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CryptoCurrencyViewSet, NewsViewSet

router = DefaultRouter()
router.register(r'cryptos', CryptoCurrencyViewSet, basename='crypto')
router.register(r'news', NewsViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
]