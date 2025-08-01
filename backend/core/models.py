from django.db import models

class CryptoCurrency(models.Model):
    coingecko_id = models.CharField(max_length=191, unique=True)
    symbol = models.CharField(max_length=128)
    name = models.CharField(max_length=191)
    price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    price_change_24h = models.FloatField(null=True, blank=True)
    market_cap = models.BigIntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"