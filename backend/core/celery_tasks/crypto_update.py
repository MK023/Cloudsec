import logging
from celery import shared_task
from django.db import transaction
from core.models import CryptoCurrency
from core.utils.crypto import fetch_coingecko_list
from core.utils.shutdown import register_shutdown_signal, is_shutdown_requested

logger = logging.getLogger(__name__)
register_shutdown_signal()

def _do_update_crypto_list():
    if is_shutdown_requested():
        logger.warning("Shutdown requested: aborting crypto list sync.")
        return 0
    coins = fetch_coingecko_list()
    existing_ids = set(CryptoCurrency.objects.values_list('coingecko_id', flat=True))
    new_objects = [
        CryptoCurrency(
            coingecko_id=coin['id'],
            symbol=coin['symbol'].upper(),
            name=coin['name']
        )
        for coin in coins
        if coin['id'] not in existing_ids
    ]
    if new_objects:
        with transaction.atomic():
            CryptoCurrency.objects.bulk_create(new_objects)
        logger.info(f"Aggiunte {len(new_objects)} nuove crypto.")
    else:
        logger.info("Nessuna nuova crypto da aggiungere.")
    return len(new_objects)

@shared_task
def update_crypto_list():
    if is_shutdown_requested():
        logger.warning("Shutdown requested: skipping crypto list update.")
        return 0
    num_added = _do_update_crypto_list()
    # Lancia sempre sync prezzi
    from core.celery_tasks.crypto_sync import update_cryptos
    update_cryptos.delay() # type: ignore
    return num_added