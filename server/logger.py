import logging


def setup_logger(name="MedicalAssistant"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] ---- [%(message)s]")
    ch.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger


# ✅ FIX: Removed logger.error / logger.critical calls that fired on every import
# and polluted logs with fake-looking errors
logger = setup_logger()