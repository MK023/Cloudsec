import logging
import time
import re
from celery import shared_task, states
from requests.exceptions import RequestException
from django.utils import timezone
from django.conf import settings
from core.models import CryptoCurrency
from core.utils.crypto import fetch_coingecko_market_data
from core.utils.shutdown import register_shutdown_signal, is_shutdown_requested

logger = logging.getLogger(__name__)
register_shutdown_signal()

BATCH_SIZE = getattr(settings, "COINGECKO_BATCH_SIZE", 100)
BATCH_DELAY = getattr(settings, "COINGECKO_BATCH_DELAY", 10)
VS_CURRENCY_LIST = getattr(settings, "COINGECKO_CURRENCIES", ["usd"])
MAX_RETRIES = getattr(settings, "COINGECKO_MAX_RETRIES", 5)


def is_valid_symbol(symbol):
    return bool(re.match(r'^[A-Z0-9]{2,10}$', symbol))

def _do_update_cryptos(update_state=None):
    coingecko_ids = list(
        CryptoCurrency.objects.filter(
            symbol__regex=r'^[A-Z0-9]{2,10}$'
        ).values_list('coingecko_id', flat=True)
    )
    if not coingecko_ids:
        logger.info("No cryptocurrencies to update.")
        return "No cryptocurrencies to update."
    result = {
        "updated": 0,
        "errors": 0,
        "not_found": [],
        "per_currency": {},
        "timestamp": timezone.now().isoformat(),
    }
    for vs_currency in VS_CURRENCY_LIST:
        updated = 0
        errors = 0
        not_found = []
        to_update = []
        num_batches = (len(coingecko_ids) + BATCH_SIZE - 1) // BATCH_SIZE
        for batch_idx, i in enumerate(range(0, len(coingecko_ids), BATCH_SIZE)):
            if is_shutdown_requested():
                logger.warning("Shutdown in progress: stopping after this batch.")
                break
            batch_ids = coingecko_ids[i:i+BATCH_SIZE]
            retries = 0
            while retries <= MAX_RETRIES:
                try:
                    data = fetch_coingecko_market_data(batch_ids, vs_currency)
                    if not isinstance(data, list):
                        logger.error(f"Unexpected response from CoinGecko: {data}")
                        errors += len(batch_ids)
                        break
                    for coin in data:
                        try:
                            crypto = CryptoCurrency.objects.get(coingecko_id=coin['id'])
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
                            not_found.append(coin['id'])
                            logger.warning(f"Crypto {coin['id']} not found in DB.")
                    if to_update:
                        CryptoCurrency.objects.bulk_update(
                            to_update, ['price', 'price_change_24h', 'market_cap', 'last_updated']
                        )
                        to_update.clear()
                    break
                except RequestException as e:
                    retries += 1
                    logger.error(f"Error fetching data from CoinGecko (retry {retries}/{MAX_RETRIES}): {e}")
                    if update_state:
                        update_state(state=states.RETRY, meta={'exc': str(e)})
                    sleep_time = min(BATCH_DELAY * (2 ** retries), 60)
                    logger.info(f"Waiting {sleep_time:.1f}s before retrying batch...")
                    time.sleep(sleep_time)
            else:
                logger.error(f"Max retries exceeded for batch {batch_idx+1}/{num_batches} (vs_currency={vs_currency})")
            if update_state:
                update_state(
                    state=states.STARTED,
                    meta={
                        'currency': vs_currency,
                        'batch': batch_idx + 1,
                        'updated': updated,
                        'errors': errors,
                        'shutdown': is_shutdown_requested(),
                    }
                )
            if not is_shutdown_requested() and batch_idx < num_batches - 1:
                time.sleep(BATCH_DELAY)
        result["updated"] += updated
        result["errors"] += errors
        result["not_found"].extend(not_found)
        result["per_currency"][vs_currency] = {
            "updated": updated,
            "errors": errors,
            "not_found": not_found,
        }
        if is_shutdown_requested():
            logger.warning("Worker stopped gracefully after shutdown signal.")
            break
    logger.info(f"Crypto update result: {result}")
    return result

@shared_task(bind=True, autoretry_for=(RequestException,), retry_backoff=True, retry_kwargs={'max_retries': MAX_RETRIES})
def update_cryptos(self):
    return _do_update_cryptos(update_state=self.update_state)