import os
from logging import getLogger

LOGGER = getLogger(__name__)


class Config:
    """Configuration manager for Streamrip Bot"""

    # Required settings
    BOT_TOKEN = ""
    OWNER_ID = 0
    TELEGRAM_API = 0
    TELEGRAM_HASH = ""

    # Optional settings
    DATABASE_URL = ""
    TG_PROXY = {}
    USER_SESSION_STRING = ""
    CMD_SUFFIX = ""
    AUTHORIZED_CHATS = ""
    SUDO_USERS = ""

    # Download settings
    DOWNLOAD_DIR = "/usr/src/app/downloads/"
    LEECH_SPLIT_SIZE = 0
    AS_DOCUMENT = False
    MEDIA_GROUP = False

    # Streamrip settings
    STREAMRIP_ENABLED = True
    STREAMRIP_CONCURRENT_DOWNLOADS = 4
    STREAMRIP_MAX_SEARCH_RESULTS = 20
    STREAMRIP_ENABLE_DATABASE = True
    STREAMRIP_AUTO_CONVERT = True

    # Quality settings
    STREAMRIP_DEFAULT_QUALITY = 3
    STREAMRIP_FALLBACK_QUALITY = 2
    STREAMRIP_DEFAULT_CODEC = "flac"
    STREAMRIP_SUPPORTED_CODECS = ["flac", "mp3", "m4a", "ogg", "opus"]
    STREAMRIP_QUALITY_FALLBACK_ENABLED = True

    # Platform settings
    STREAMRIP_QOBUZ_ENABLED = True
    STREAMRIP_QOBUZ_QUALITY = 3
    STREAMRIP_TIDAL_ENABLED = True
    STREAMRIP_TIDAL_QUALITY = 3
    STREAMRIP_DEEZER_ENABLED = True
    STREAMRIP_DEEZER_QUALITY = 2
    STREAMRIP_SOUNDCLOUD_ENABLED = True
    STREAMRIP_SOUNDCLOUD_QUALITY = 0
    STREAMRIP_LASTFM_ENABLED = True
    STREAMRIP_YOUTUBE_QUALITY = 0

    # Authentication
    STREAMRIP_QOBUZ_EMAIL = ""
    STREAMRIP_QOBUZ_PASSWORD = ""
    STREAMRIP_QOBUZ_APP_ID = ""
    STREAMRIP_QOBUZ_SECRETS = []
    STREAMRIP_TIDAL_ACCESS_TOKEN = ""
    STREAMRIP_TIDAL_REFRESH_TOKEN = ""
    STREAMRIP_TIDAL_USER_ID = ""
    STREAMRIP_TIDAL_COUNTRY_CODE = ""
    STREAMRIP_TIDAL_TOKEN_EXPIRY = ""
    STREAMRIP_TIDAL_EMAIL = ""
    STREAMRIP_TIDAL_PASSWORD = ""
    STREAMRIP_DEEZER_ARL = ""
    STREAMRIP_SOUNDCLOUD_CLIENT_ID = ""
    STREAMRIP_SOUNDCLOUD_APP_VERSION = ""

    # Advanced features
    STREAMRIP_METADATA_EXCLUDE = []
    STREAMRIP_FILENAME_TEMPLATE = ""
    STREAMRIP_FOLDER_TEMPLATE = ""
    STREAMRIP_EMBED_COVER_ART = True
    STREAMRIP_SAVE_COVER_ART = True
    STREAMRIP_COVER_ART_SIZE = "large"

    # Download configuration
    STREAMRIP_MAX_CONNECTIONS = 6
    STREAMRIP_REQUESTS_PER_MINUTE = 60
    STREAMRIP_SOURCE_SUBDIRECTORIES = False
    STREAMRIP_DISC_SUBDIRECTORIES = True
    STREAMRIP_CONCURRENCY = True
    STREAMRIP_VERIFY_SSL = True

    # Platform-specific
    STREAMRIP_QOBUZ_DOWNLOAD_BOOKLETS = True
    STREAMRIP_QOBUZ_USE_AUTH_TOKEN = False
    STREAMRIP_TIDAL_DOWNLOAD_VIDEOS = True
    STREAMRIP_DEEZER_USE_DEEZLOADER = True
    STREAMRIP_DEEZER_DEEZLOADER_WARNINGS = True
    STREAMRIP_YOUTUBE_DOWNLOAD_VIDEOS = False

    # Database
    STREAMRIP_DATABASE_DOWNLOADS_ENABLED = True
    STREAMRIP_DATABASE_DOWNLOADS_PATH = "./downloads.db"
    STREAMRIP_DATABASE_FAILED_DOWNLOADS_ENABLED = True
    STREAMRIP_DATABASE_FAILED_DOWNLOADS_PATH = "./failed_downloads.db"

    # Conversion
    STREAMRIP_CONVERSION_ENABLED = False
    STREAMRIP_CONVERSION_CODEC = "ALAC"
    STREAMRIP_CONVERSION_SAMPLING_RATE = 48000
    STREAMRIP_CONVERSION_BIT_DEPTH = 24
    STREAMRIP_CONVERSION_LOSSY_BITRATE = 320

    # File paths
    STREAMRIP_FILEPATHS_ADD_SINGLES_TO_FOLDER = False
    STREAMRIP_FILEPATHS_FOLDER_FORMAT = "{albumartist} - {title} ({year}) [{container}] [{bit_depth}B-{sampling_rate}kHz]"
    STREAMRIP_FILEPATHS_TRACK_FORMAT = (
        "{tracknumber:02}. {artist} - {title}{explicit}"
    )
    STREAMRIP_FILEPATHS_RESTRICT_CHARACTERS = False
    STREAMRIP_FILEPATHS_TRUNCATE_TO = 120

    # Last.fm
    STREAMRIP_LASTFM_SOURCE = "qobuz"
    STREAMRIP_LASTFM_FALLBACK_SOURCE = ""
    STREAMRIP_CLI_TEXT_OUTPUT = True
    STREAMRIP_CLI_PROGRESS_BARS = False
    STREAMRIP_CLI_MAX_SEARCH_RESULTS = 200

    # Miscellaneous
    STREAMRIP_MISC_CHECK_FOR_UPDATES = True
    STREAMRIP_MISC_VERSION = "2.0.6"

    # Limits
    STREAMRIP_LIMIT = 0
    DAILY_TASK_LIMIT = 0
    USER_MAX_TASKS = 0
    BOT_MAX_TASKS = 0

    # Status
    STATUS_UPDATE_INTERVAL = 3
    STATUS_LIMIT = 10

    # Logging
    LOG_CHAT_ID = 0

    @classmethod
    def load(cls):
        """Load configuration from environment variables or config file"""
        try:
            # Try to import config file
            import config

            for attr in dir(config):
                if not attr.startswith("_"):
                    setattr(cls, attr, getattr(config, attr))
        except ImportError:
            LOGGER.warning("config.py not found, using environment variables")

        # Override with environment variables
        cls._load_from_env()

        # Validate required settings
        cls._validate_config()

    @classmethod
    def _load_from_env(cls):
        """Load configuration from environment variables"""
        # Required settings
        cls.BOT_TOKEN = os.environ.get("BOT_TOKEN", cls.BOT_TOKEN)
        cls.OWNER_ID = int(os.environ.get("OWNER_ID", cls.OWNER_ID))
        cls.TELEGRAM_API = int(os.environ.get("TELEGRAM_API", cls.TELEGRAM_API))
        cls.TELEGRAM_HASH = os.environ.get("TELEGRAM_HASH", cls.TELEGRAM_HASH)

        # Optional settings
        cls.DATABASE_URL = os.environ.get("DATABASE_URL", cls.DATABASE_URL)
        cls.USER_SESSION_STRING = os.environ.get(
            "USER_SESSION_STRING", cls.USER_SESSION_STRING
        )
        cls.CMD_SUFFIX = os.environ.get("CMD_SUFFIX", cls.CMD_SUFFIX)
        cls.AUTHORIZED_CHATS = os.environ.get(
            "AUTHORIZED_CHATS", cls.AUTHORIZED_CHATS
        )
        cls.SUDO_USERS = os.environ.get("SUDO_USERS", cls.SUDO_USERS)

        # Download settings
        cls.DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", cls.DOWNLOAD_DIR)
        cls.LEECH_SPLIT_SIZE = int(
            os.environ.get("LEECH_SPLIT_SIZE", cls.LEECH_SPLIT_SIZE)
        )
        cls.AS_DOCUMENT = (
            os.environ.get("AS_DOCUMENT", str(cls.AS_DOCUMENT)).lower() == "true"
        )
        cls.MEDIA_GROUP = (
            os.environ.get("MEDIA_GROUP", str(cls.MEDIA_GROUP)).lower() == "true"
        )

        # Streamrip settings
        cls.STREAMRIP_ENABLED = (
            os.environ.get("STREAMRIP_ENABLED", str(cls.STREAMRIP_ENABLED)).lower()
            == "true"
        )
        cls.STREAMRIP_CONCURRENT_DOWNLOADS = int(
            os.environ.get(
                "STREAMRIP_CONCURRENT_DOWNLOADS", cls.STREAMRIP_CONCURRENT_DOWNLOADS
            )
        )
        cls.STREAMRIP_MAX_SEARCH_RESULTS = int(
            os.environ.get(
                "STREAMRIP_MAX_SEARCH_RESULTS", cls.STREAMRIP_MAX_SEARCH_RESULTS
            )
        )

        # Authentication
        cls.STREAMRIP_QOBUZ_EMAIL = os.environ.get(
            "STREAMRIP_QOBUZ_EMAIL", cls.STREAMRIP_QOBUZ_EMAIL
        )
        cls.STREAMRIP_QOBUZ_PASSWORD = os.environ.get(
            "STREAMRIP_QOBUZ_PASSWORD", cls.STREAMRIP_QOBUZ_PASSWORD
        )
        cls.STREAMRIP_TIDAL_ACCESS_TOKEN = os.environ.get(
            "STREAMRIP_TIDAL_ACCESS_TOKEN", cls.STREAMRIP_TIDAL_ACCESS_TOKEN
        )
        cls.STREAMRIP_TIDAL_REFRESH_TOKEN = os.environ.get(
            "STREAMRIP_TIDAL_REFRESH_TOKEN", cls.STREAMRIP_TIDAL_REFRESH_TOKEN
        )
        cls.STREAMRIP_DEEZER_ARL = os.environ.get(
            "STREAMRIP_DEEZER_ARL", cls.STREAMRIP_DEEZER_ARL
        )

        # Limits
        cls.STREAMRIP_LIMIT = int(
            os.environ.get("STREAMRIP_LIMIT", cls.STREAMRIP_LIMIT)
        )
        cls.DAILY_TASK_LIMIT = int(
            os.environ.get("DAILY_TASK_LIMIT", cls.DAILY_TASK_LIMIT)
        )
        cls.USER_MAX_TASKS = int(
            os.environ.get("USER_MAX_TASKS", cls.USER_MAX_TASKS)
        )
        cls.BOT_MAX_TASKS = int(os.environ.get("BOT_MAX_TASKS", cls.BOT_MAX_TASKS))

        # Status
        cls.STATUS_UPDATE_INTERVAL = int(
            os.environ.get("STATUS_UPDATE_INTERVAL", cls.STATUS_UPDATE_INTERVAL)
        )
        cls.STATUS_LIMIT = int(os.environ.get("STATUS_LIMIT", cls.STATUS_LIMIT))

        # Logging
        cls.LOG_CHAT_ID = int(os.environ.get("LOG_CHAT_ID", cls.LOG_CHAT_ID))

    @classmethod
    def _validate_config(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.OWNER_ID:
            raise ValueError("OWNER_ID is required")
        if not cls.TELEGRAM_API:
            raise ValueError("TELEGRAM_API is required")
        if not cls.TELEGRAM_HASH:
            raise ValueError("TELEGRAM_HASH is required")

        LOGGER.info("Configuration loaded successfully")
