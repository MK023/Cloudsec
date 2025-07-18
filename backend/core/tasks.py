from celery import shared_task
import requests
from .models import CryptoCurrency
from django.utils import timezone

@shared_task
def update_cryptos():
    # Prendi tutti i coingecko_id presenti nel db
    coingecko_ids = list(CryptoCurrency.objects.values_list('coingecko_id', flat=True))
    if not coingecko_ids:
        return "No cryptocurrencies to update."

    # CoinGecko accetta massimo 250 id per chiamata, quindi eventualmente spezza in batch
    batch_size = 200
    updated = 0

    for i in range(0, len(coingecko_ids), batch_size):
        batch_ids = coingecko_ids[i:i+batch_size]
        ids_str = ','.join(batch_ids)
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'ids': ids_str,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for coin in data:
                try:
                    crypto = CryptoCurrency.objects.get(coingecko_id=coin['id'])
                    crypto.price = coin.get('current_price')
                    crypto.price_change_24h = coin.get('price_change_percentage_24h')
                    crypto.market_cap = coin.get('market_cap')
                    crypto.last_updated = timezone.now()
                    crypto.save()
                    updated += 1
                except CryptoCurrency.DoesNotExist:
                    continue
        else:
            print(f"Errore CoinGecko: {response.status_code} - {response.content}")

    return f"Updated {updated} cryptocurrencies"