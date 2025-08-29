from django.contrib import admin

from .models import CryptoCurrency, News


@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "price", "market_cap", "last_updated")
    search_fields = ("name", "symbol", "coingecko_id")

    # Mostra solo le crypto con market cap significativo (>10 milioni, ad esempio)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(market_cap__gte=10000000)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "published_at")
    search_fields = ("title", "source", "summary")
    autocomplete_fields = ["cryptos"]
    list_filter = ("source", "published_at")
