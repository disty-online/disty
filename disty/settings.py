import os
import logging

DEFAULT_DOWNLOAD_LIMIT = int(os.environ.get("DEFAULT_DOWNLOAD_LIMIT", 1))
DEFAULT_DOWNLOAD_EXPIRY_DAYS = int(os.environ.get("DEFAULT_DOWNLOAD_EXPIRY_DAYS", 1))
DEFAULT_UPLOAD_URL_EXPIRY_DAYS = int(
    os.environ.get("DEFAULT_UPLOAD_URL_EXPIRY_DAYS", 10)
)
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "documents/")

level = logging.DEBUG if os.environ.get("DEBUG", None) else logging.INFO

logger = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=level,
    datefmt="[%d/%b/%Y %H:%M:%S]",
)
