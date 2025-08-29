from rest_framework import filters, viewsets

from .models import CryptoCurrency, News
from .serializers import CryptoCurrencySerializer, NewsSerializer


class CryptoCurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CryptoCurrency.objects.all()
    serializer_class = CryptoCurrencySerializer
    lookup_field = "symbol"  # Consente di usare /api/cryptos/BTC/


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.prefetch_related("cryptos").order_by("-published_at")
    serializer_class = NewsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "title",
        "summary",
        "source",
        "author",
        "cryptos__symbol",
        "cryptos__name",
    ]
    ordering_fields = ["published_at", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        crypto = self.request.query_params.get("crypto")
        if crypto:
            qs = qs.filter(cryptos__symbol__iexact=crypto)
        date_from = self.request.query_params.get("from")
        if date_from:
            qs = qs.filter(published_at__gte=date_from)
        return qs


import redis
from django.conf import settings

# La funzione healthz resta invariata
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def healthz(request):
    db_ok = True
    redis_ok = True

    try:
        connections["default"].cursor()
    except OperationalError:
        db_ok = False

    try:
        redis_url = settings.CELERY_BROKER_URL or settings.REDIS_URL or "redis://localhost:6379/0"
        r = redis.Redis.from_url(redis_url)
        r.ping()
    except Exception:
        redis_ok = False

    overall_ok = db_ok and redis_ok
    status = 200 if overall_ok else 500
    return JsonResponse(
        {
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
            "status": "ok" if overall_ok else "error",
        },
        status=status,
    )
