import logging
import signal

logger = logging.getLogger(__name__)

_shutdown_requested = False


def handle_shutdown(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True
    logger.warning("Graceful shutdown requested. Will finish current job then exit.")


def register_shutdown_signal():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)


def is_shutdown_requested():
    return _shutdown_requested
