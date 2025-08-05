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

class News(models.Model):
    title = models.CharField(max_length=300)
    source = models.CharField(max_length=100)
    author = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField()
    urlToImage = models.URLField(blank=True, null=True)
    published_at = models.DateTimeField()
    summary = models.TextField(blank=True)
    cryptos = models.ManyToManyField(CryptoCurrency, related_name='news')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Visualizza i simboli associati
        return f"{self.title} | {[c.symbol for c in self.cryptos.all()]}"