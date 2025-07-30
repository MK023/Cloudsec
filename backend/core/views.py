from rest_framework import viewsets
from .models import CryptoCurrency
from .serializers import CryptoCurrencySerializer

class CryptoCurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoCurrency.objects.all()
    serializer_class = CryptoCurrencySerializer
    lookup_field = 'symbol'  # Consente di usare /api/cryptos/BTC/
    
    
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.conf import settings

import redis

def healthz(request):
    db_ok = True
    redis_ok = True

    # Check PostgreSQL
    try:
        connections['default'].cursor()
    except OperationalError:
        db_ok = False

    # Check Redis
    try:
        redis_url = settings.CELERY_BROKER_URL or settings.REDIS_URL or "redis://localhost:6379/0"
        r = redis.Redis.from_url(redis_url)
        r.ping()
    except Exception:
        redis_ok = False

    overall_ok = db_ok and redis_ok
    status = 200 if overall_ok else 500
    return JsonResponse({
        'database': 'ok' if db_ok else 'error',
        'redis': 'ok' if redis_ok else 'error',
        'status': 'ok' if overall_ok else 'error'
    }, status=status)