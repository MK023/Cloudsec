from rest_framework import viewsets
from .models import CryptoCurrency
from .serializers import CryptoCurrencySerializer

class CryptoCurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoCurrency.objects.all()
    serializer_class = CryptoCurrencySerializer
    lookup_field = 'symbol'  # Consente di usare /api/cryptos/BTC/