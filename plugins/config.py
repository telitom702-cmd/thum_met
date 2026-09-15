import os
from os import environ, getenv
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

class Config(object):
    
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8721504696:AAEIop-Ye5m1hF_k4VfZkPWBLhfBdvxkAvI")
    API_ID = int(os.environ.get("API_ID", "24776633"))
    API_HASH = os.environ.get("API_HASH", "8823668328:AAEHQyUmGYBuu-d8BoHOvqE4OYp4sPxqjOs")
    
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    MAX_FILE_SIZE = 2194304000
    TG_MAX_FILE_SIZE = 2194304000
    FREE_USER_MAX_FILE_SIZE = 2194304000
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))
    DEF_THUMB_NAIL_VID_S = os.environ.get("DEF_THUMB_NAIL_VID_S", "https://placehold.it/90x90")
    HTTP_PROXY = os.environ.get("HTTP_PROXY", "")
    
    OUO_IO_API_KEY = ""
    MAX_MESSAGE_LENGTH = 4096
    PROCESS_MAX_TIMEOUT = 3600
    DEF_WATER_MARK_FILE = "@UploaderXNTBot"

    ADMIN = set(
        int(x) for x in environ.get("ADMIN", "8248792819").split()
        if x.isdigit()
    )

    BANNED_USERS = set(
        int(x) for x in environ.get("BANNED_USERS", "").split()
        if x.isdigit()
    )

    DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://rendamd1_db_user:M7vb8ZD9rx0AfHnP@cluster0.uzqvib6.mongodb.net/?appName=Cluster0")

    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003084490680"))
    LOGGER = logging
    OWNER_ID = int(os.environ.get("OWNER_ID", "8248792819"))
    SESSION_NAME = "UploaderXNTBot"
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "-1004468070238")

    TG_MIN_FILE_SIZE = 2194304000
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "Jacjacc")
    ADL_BOT_RQ = {}

    # Set False off else True
    TRUE_OR_FALSE = os.environ.get("TRUE_OR_FALSE", "").lower() == "true"

    # Shortlink settings
    SHORT_DOMAIN = environ.get("SHORT_DOMAIN", "")
    SHORT_API = environ.get("SHORT_API", "")

    # Verification video link
    VERIFICATION = os.environ.get("VERIFICATION", "")

    
