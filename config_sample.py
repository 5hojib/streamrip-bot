# REQUIRED CONFIG
BOT_TOKEN = ""  # Get this from @BotFather
OWNER_ID = 0  # Your Telegram User ID (not username) as an integer
TELEGRAM_API = 0  # Get this from my.telegram.org
TELEGRAM_HASH = ""  # Get this from my.telegram.org

# SEMI-REQUIRED, WE SUGGEST TO FILL IT FROM MONGODB
DATABASE_URL = ""  # MongoDB URI for storing user data and preferences

# OPTIONAL CONFIG
TG_PROXY = {}  # Proxy for Telegram connection, format: {'addr': 'ip:port', 'username': 'username', 'password': 'password'}
USER_SESSION_STRING = ""  # Pyrogram user session string for mirror/leech authentication

CMD_SUFFIX = ""  # Command suffix to distinguish commands, e.g. "1" would make commands like /mirror1
AUTHORIZED_CHATS = ""  # List of authorized chat IDs where the bot can be used, separated by space
SUDO_USERS = ""  # List of sudo user IDs who can use admin commands, separated by space

# Download Settings
DOWNLOAD_DIR = "/usr/src/app/downloads/"  # Directory where files will be downloaded
LEECH_SPLIT_SIZE = 0  # Size of split files in bytes, 0 means no split
AS_DOCUMENT = False  # Send files as documents instead of media
MEDIA_GROUP = False  # Group media files together when sending

# Streamrip Settings
STREAMRIP_ENABLED = True  # Enable/disable streamrip feature
STREAMRIP_CONCURRENT_DOWNLOADS = 4  # Concurrent downloads per platform
STREAMRIP_MAX_SEARCH_RESULTS = 20  # Search results limit
STREAMRIP_ENABLE_DATABASE = True  # Enable download history tracking
STREAMRIP_AUTO_CONVERT = True  # Enable automatic format conversion

# Streamrip Quality and Format Settings
STREAMRIP_DEFAULT_QUALITY = 3  # Default quality (0-4: 0=128kbps, 1=320kbps, 2=CD, 3=Hi-Res, 4=Hi-Res+)
STREAMRIP_FALLBACK_QUALITY = 2  # Fallback if preferred quality unavailable
STREAMRIP_DEFAULT_CODEC = "flac"  # Default output format
STREAMRIP_SUPPORTED_CODECS = ["flac", "mp3", "m4a", "ogg", "opus"]  # Available formats
STREAMRIP_QUALITY_FALLBACK_ENABLED = True  # Auto-fallback to lower quality

# Streamrip Platform Settings
STREAMRIP_QOBUZ_ENABLED = True  # Enable Qobuz downloads
STREAMRIP_QOBUZ_QUALITY = 3  # Qobuz quality level (0-3)
STREAMRIP_TIDAL_ENABLED = True  # Enable Tidal downloads
STREAMRIP_TIDAL_QUALITY = 3  # Tidal quality level (0-3)
STREAMRIP_DEEZER_ENABLED = True  # Enable Deezer downloads
STREAMRIP_DEEZER_QUALITY = 2  # Deezer quality level (0-2)
STREAMRIP_SOUNDCLOUD_ENABLED = True  # Enable SoundCloud downloads
STREAMRIP_SOUNDCLOUD_QUALITY = 0  # SoundCloud quality level
STREAMRIP_LASTFM_ENABLED = True  # Enable Last.fm playlist conversion
STREAMRIP_YOUTUBE_QUALITY = 0  # YouTube quality level

# Streamrip Authentication (stored securely in database)
# Qobuz - Highest quality platform (up to 24-bit/192kHz)
STREAMRIP_QOBUZ_EMAIL = ""  # Qobuz account email
STREAMRIP_QOBUZ_PASSWORD = ""  # Qobuz account password
STREAMRIP_QOBUZ_APP_ID = ""  # Qobuz app ID
STREAMRIP_QOBUZ_SECRETS = []  # Qobuz secrets array

# Tidal - Hi-Res/MQA platform (OAuth tokens preferred)
STREAMRIP_TIDAL_ACCESS_TOKEN = ""  # Tidal access token
STREAMRIP_TIDAL_REFRESH_TOKEN = ""  # Tidal refresh token
STREAMRIP_TIDAL_USER_ID = ""  # Tidal user ID
STREAMRIP_TIDAL_COUNTRY_CODE = ""  # Tidal country code (e.g., 'US')
STREAMRIP_TIDAL_TOKEN_EXPIRY = ""  # Tidal token expiry timestamp (optional)
# Fallback authentication (limited functionality)
STREAMRIP_TIDAL_EMAIL = ""  # Tidal email (fallback method)
STREAMRIP_TIDAL_PASSWORD = ""  # Tidal password (fallback method)

# Deezer - CD quality platform
STREAMRIP_DEEZER_ARL = ""  # Deezer ARL cookie (get from browser cookies)

# SoundCloud - Free platform (optional authentication)
STREAMRIP_SOUNDCLOUD_CLIENT_ID = ""  # SoundCloud client ID (optional)
STREAMRIP_SOUNDCLOUD_APP_VERSION = ""  # SoundCloud app version (optional)

# Streamrip Advanced Features
STREAMRIP_METADATA_EXCLUDE = []  # Metadata tags to exclude
STREAMRIP_FILENAME_TEMPLATE = ""  # Custom filename template
STREAMRIP_FOLDER_TEMPLATE = ""  # Custom folder structure template
STREAMRIP_EMBED_COVER_ART = True  # Embed album artwork in files
STREAMRIP_SAVE_COVER_ART = True  # Save separate cover art files
STREAMRIP_COVER_ART_SIZE = "large"  # Cover art size preference

# Streamrip Download Configuration
STREAMRIP_MAX_CONNECTIONS = 6  # Maximum connections per download
STREAMRIP_REQUESTS_PER_MINUTE = 60  # API requests per minute limit
STREAMRIP_SOURCE_SUBDIRECTORIES = False  # Create source subdirectories
STREAMRIP_DISC_SUBDIRECTORIES = True  # Create disc subdirectories
STREAMRIP_CONCURRENCY = True  # Enable concurrent downloads
STREAMRIP_VERIFY_SSL = True  # Verify SSL certificates

# Streamrip Platform-Specific Configuration
STREAMRIP_QOBUZ_DOWNLOAD_BOOKLETS = True  # Download PDF booklets from Qobuz
STREAMRIP_QOBUZ_USE_AUTH_TOKEN = False  # Use authentication token for Qobuz
STREAMRIP_TIDAL_DOWNLOAD_VIDEOS = True  # Download videos from Tidal
STREAMRIP_DEEZER_USE_DEEZLOADER = True  # Use Deezloader for Deezer
STREAMRIP_DEEZER_DEEZLOADER_WARNINGS = True  # Show Deezloader warnings
STREAMRIP_YOUTUBE_DOWNLOAD_VIDEOS = False  # Download videos from YouTube

# Streamrip Database Configuration
STREAMRIP_DATABASE_DOWNLOADS_ENABLED = True  # Enable downloads database
STREAMRIP_DATABASE_DOWNLOADS_PATH = "./downloads.db"  # Downloads database path
STREAMRIP_DATABASE_FAILED_DOWNLOADS_ENABLED = True  # Enable failed downloads database
STREAMRIP_DATABASE_FAILED_DOWNLOADS_PATH = "./failed_downloads.db"  # Failed downloads database path

# Streamrip Conversion Configuration
STREAMRIP_CONVERSION_ENABLED = False  # Enable format conversion
STREAMRIP_CONVERSION_CODEC = "ALAC"  # Conversion codec
STREAMRIP_CONVERSION_SAMPLING_RATE = 48000  # Conversion sampling rate
STREAMRIP_CONVERSION_BIT_DEPTH = 24  # Conversion bit depth
STREAMRIP_CONVERSION_LOSSY_BITRATE = 320  # Lossy conversion bitrate

# Streamrip File Paths and Naming
STREAMRIP_FILEPATHS_ADD_SINGLES_TO_FOLDER = False  # Add singles to folder
STREAMRIP_FILEPATHS_FOLDER_FORMAT = "{albumartist} - {title} ({year}) [{container}] [{bit_depth}B-{sampling_rate}kHz]"  # Folder naming format template
STREAMRIP_FILEPATHS_TRACK_FORMAT = "{tracknumber:02}. {artist} - {title}{explicit}"  # Track naming format template
STREAMRIP_FILEPATHS_RESTRICT_CHARACTERS = False  # Restrict special characters in filenames
STREAMRIP_FILEPATHS_TRUNCATE_TO = 120  # Truncate filenames to length

# Streamrip Last.fm and CLI Configuration
STREAMRIP_LASTFM_SOURCE = "qobuz"  # Last.fm source platform
STREAMRIP_LASTFM_FALLBACK_SOURCE = ""  # Last.fm fallback source platform
STREAMRIP_CLI_TEXT_OUTPUT = True  # Enable CLI text output
STREAMRIP_CLI_PROGRESS_BARS = False  # Show CLI progress bars (disabled for bot)
STREAMRIP_CLI_MAX_SEARCH_RESULTS = 200  # Max CLI search results

# Streamrip Miscellaneous
STREAMRIP_MISC_CHECK_FOR_UPDATES = True  # Check for streamrip updates
STREAMRIP_MISC_VERSION = "2.0.6"  # Streamrip version

# Limits Settings
STREAMRIP_LIMIT = 0  # Maximum size for streamrip downloads in GB (0 = unlimited)
DAILY_TASK_LIMIT = 0  # Maximum number of tasks per day per user (0 = unlimited)
USER_MAX_TASKS = 0  # Maximum concurrent tasks per user (0 = unlimited)
BOT_MAX_TASKS = 0  # Maximum number of concurrent tasks the bot can handle (0 = unlimited)

# Status Settings
STATUS_UPDATE_INTERVAL = 3  # Status update interval in seconds (minimum 2, recommended: 3-5)
STATUS_LIMIT = 10  # Number of tasks to display in status message (recommended: 4-10)

# Logging
LOG_CHAT_ID = 0  # Chat ID where logs will be sent
