import logging
from celery import shared_task
from core.utils.news_importer import import_news_from_newsapi

logger = logging.getLogger(__name__)

@shared_task(name="core.celery_tasks.news_sync.update_news")
def update_news(query="crypto"):
    """
    Task Celery per scaricare e importare news da NewsAPI,
    associando ogni news alle crypto menzionate.
    Il parametro 'query' può essere usato per personalizzare la ricerca.
    """
    try:
        created_count = import_news_from_newsapi(query=query)
        logger.info(f"NewsAPI sync: {created_count} nuove news importate.")
        return created_count
    except Exception as e:
        logger.error(f"Errore durante la sync di NewsAPI: {e}", exc_info=True)
        return 0