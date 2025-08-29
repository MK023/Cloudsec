"""
Scopo:
File di funzioni di utilità (helper) che incapsulano la logica di chiamata alle API CoinGecko.

Funzionalità:
Funzioni per scaricare la lista delle crypto.
Funzioni per scaricare i dati di mercato per batch.
Separando qui la logica di fetch/parsing, i task sono più puliti e facilmente testabili.
Se vuoi fare test, modifichi solo qui.

"""

import logging
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_coingecko_list():
    """
    Restituisce la lista di tutte le crypto da CoinGecko.
    """
    url = settings.COINGECKO_LIST_URL
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_coingecko_market_data(ids, vs_currency):
    """
    Restituisce i dati di mercato per una lista di coingecko_id e una valuta.
    Gestisce retry e rate-limit.
    """
    url = settings.COINGECKO_MARKET_URL
    ids_str = ",".join(ids)
    params = {
        "vs_currency": vs_currency,
        "ids": ids_str,
    }
    for attempt in range(settings.COINGECKO_MAX_RETRIES):
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 429:
            logger.warning("Rate limit reached (429). Waiting extra 10 seconds before retrying batch.")
            time.sleep(10)
            continue
        try:
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching market data from CoinGecko (attempt {attempt + 1}): {e}")
            if attempt == settings.COINGECKO_MAX_RETRIES - 1:
                raise
            time.sleep(3)
    return []
