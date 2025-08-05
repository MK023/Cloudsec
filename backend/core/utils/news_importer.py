import requests
from django.utils.dateparse import parse_datetime
from ..models import News, CryptoCurrency

def match_cryptos_to_news(article, crypto_queryset):
    """
    Per ogni notizia, restituisce una lista di CryptoCurrency che compaiono
    nel titolo, description o content della news.
    """
    matches = []
    text_fields = [
        article.get('title', ''),
        article.get('description', ''),
        article.get('content', ''),
    ]
    for crypto in crypto_queryset:
        for text in text_fields:
            # Cerca sia il symbol che il name, case insensitive
            if crypto.symbol.lower() in text.lower() or crypto.name.lower() in text.lower():
                matches.append(crypto)
                break
    return matches

def import_news_from_newsapi(api_key, query="crypto", page_size=20):
    """
    1. Scarica le news da NewsAPI su un certo argomento.
    2. Per ogni news, cerca tutte le crypto menzionate nel testo.
    3. Crea la News e collega tutte le crypto trovate (relazione ManyToMany).
    4. Salta le news già esistenti (usa l'URL come chiave univoca).
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": page_size,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "publishedAt",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    articles = response.json().get("articles", [])
    crypto_queryset = CryptoCurrency.objects.all()

    created_count = 0
    for article in articles:
        matches = match_cryptos_to_news(article, crypto_queryset)
        if not matches:
            continue

        # Evita i duplicati: controlla se la news esiste già usando l'URL
        if News.objects.filter(url=article['url']).exists():
            continue

        news = News.objects.create(
            title=article.get('title', '')[:300],
            source=article.get('source', {}).get('name', '')[:100],
            author=article.get('author', '')[:100] if article.get('author') else None,
            url=article['url'],
            urlToImage=article.get('urlToImage'),
            published_at=parse_datetime(article['publishedAt']),
            summary=article.get('description', ''),
        )
        news.cryptos.set(matches)
        created_count += 1

    return created_count