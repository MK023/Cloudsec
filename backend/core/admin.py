from django.contrib import admin
from .models import CryptoCurrency

class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "price", "market_cap", "last_updated")
    search_fields = ("name", "symbol", "coingecko_id")

admin.site.register(CryptoCurrency, CryptoCurrencyAdmin)