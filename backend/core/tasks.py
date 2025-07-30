from celery import shared_task, states
import requests
from requests.exceptions import RequestException
from .models import CryptoCurrency
from django.utils import timezone
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)

# Parametri configurabili da settings
BATCH_SIZE = getattr(settings, "COINGECKO_BATCH_SIZE", 200)
BATCH_DELAY = getattr(settings, "COINGECKO_BATCH_DELAY", 1.5)  # secondi tra batch
VS_CURRENCY_LIST = getattr(settings, "COINGECKO_CURRENCIES", ["usd"])  # lista per multi-currency
MAX_RETRIES = getattr(settings, "COINGECKO_MAX_RETRIES", 5)

@shared_task(bind=True, autoretry_for=(RequestException,), retry_backoff=True, retry_kwargs={'max_retries': MAX_RETRIES})
def update_cryptos(self):
    coingecko_ids = list(CryptoCurrency.objects.values_list('coingecko_id', flat=True))
    if not coingecko_ids:
        logger.info("No cryptocurrencies to update.")
        return "No cryptocurrencies to update."

    total_updated = 0
    total_errors = 0
    not_found = []
    per_currency_results = {}

    for vs_currency in VS_CURRENCY_LIST:
        updated = 0
        errors = 0
        currency_not_found = []
        to_update = []
        
        for i in range(0, len(coingecko_ids), BATCH_SIZE):
            batch_ids = coingecko_ids[i:i+BATCH_SIZE]
            ids_str = ','.join(batch_ids)
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': vs_currency,
                'ids': ids_str,
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 429:
                    logger.warning("Rate limit reached (429). Waiting extra 10 seconds before retrying batch.")
                    time.sleep(10)
                    response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, list):
                    logger.error(f"Unexpected response from CoinGecko: {data}")
                    errors += len(batch_ids)
                    continue
                for coin in data:
                    try:
                        crypto = CryptoCurrency.objects.get(coingecko_id=coin['id'])
                        # Solo aggiorna se i campi sono presenti
                        price = coin.get('current_price')
                        market_cap = coin.get('market_cap')
                        price_change = coin.get('price_change_percentage_24h')
                        if price is not None and market_cap is not None:
                            crypto.price = price
                            crypto.price_change_24h = price_change
                            crypto.market_cap = market_cap
                            crypto.last_updated = timezone.now()
                            to_update.append(crypto)
                            updated += 1
                        else:
                            errors += 1
                            logger.warning(f"Missing data for {coin['id']} in CoinGecko response.")
                    except CryptoCurrency.DoesNotExist:
                        errors += 1
                        currency_not_found.append(coin['id'])
                        logger.warning(f"Crypto {coin['id']} not found in DB.")
                if to_update:
                    CryptoCurrency.objects.bulk_update(
                        to_update, ['price', 'price_change_24h', 'market_cap', 'last_updated']
                    )
                    to_update.clear()
                # Rispetta rate-limit CoinGecko (free: max 50 req/min)
                time.sleep(BATCH_DELAY)
            except RequestException as e:
                logger.error(f"Error fetching data from CoinGecko: {e}")
                errors += len(batch_ids)
                self.update_state(state=states.RETRY, meta={'exc': str(e)})
                raise  # trigger retry

            # Progress tracking opzionale
            self.update_state(
                state=states.STARTED,
                meta={'currency': vs_currency, 
                      'batch': i//BATCH_SIZE + 1, 
                      'updated': updated, 
                      'errors': errors}
            )

        per_currency_results[vs_currency] = {
            "updated": updated,
            "errors": errors,
            "not_found": currency_not_found,
        }
        total_updated += updated
        total_errors += errors
        not_found.extend(currency_not_found)

    result = {
        "updated": total_updated,
        "errors": total_errors,
        "not_found": not_found,
        "per_currency": per_currency_results,
        "timestamp": timezone.now().isoformat(),
    }
    logger.info(f"Crypto update result: {result}")
    return result