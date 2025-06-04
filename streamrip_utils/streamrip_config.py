from pathlib import Path
from logging import getLogger

LOGGER = getLogger(__name__)

try:
    from streamrip.config import Config as StreamripConfig

    STREAMRIP_AVAILABLE = True
except ImportError:
    STREAMRIP_AVAILABLE = False
    LOGGER.warning("Streamrip not installed. Streamrip features will be disabled.")


class StreamripConfigHelper:
    """Helper for streamrip configuration management"""

    def __init__(self):
        self.config: StreamripConfig | None = None
        self.config_path: Path | None = None
        self._initialized = False
        self._initialization_attempted = False

    async def lazy_initialize(self) -> bool:
        """Lazy initialization - only initialize when needed"""
        if self._initialized:
            return True

        if self._initialization_attempted:
            return False

        success = await self.initialize()
        self._initialization_attempted = True

        if success:
            # Enable streamrip if initialization was successful
            from config_manager import Config

            Config.STREAMRIP_ENABLED = True
        else:
            # Disable streamrip if initialization failed
            from config_manager import Config

            Config.STREAMRIP_ENABLED = False
            LOGGER.warning("❌ Streamrip disabled due to initialization failure")

        return success

    async def initialize(self) -> bool:
        """Initialize streamrip configuration"""
        if not STREAMRIP_AVAILABLE:
            LOGGER.error("Streamrip is not available")
            return False

        try:
            # Use temporary config location
            self.config_path = Path.home() / ".config" / "streamrip" / "config.toml"

            # Create config directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create default config using proper API
            try:
                # Try the newer API first
                self.config = StreamripConfig()
                LOGGER.info(
                    "Created default streamrip config using StreamripConfig()"
                )
            except Exception:
                try:
                    # Try alternative initialization
                    self.config = StreamripConfig.defaults()
                    LOGGER.info("Created default streamrip config using defaults()")
                except Exception:
                    # Fallback: create config file manually and load it
                    await self._create_default_config_file()
                    self.config = StreamripConfig.from_file(str(self.config_path))

            # Always apply bot settings to override any config values
            await self._apply_bot_settings()
            await self.save_config()

            self._initialized = True
            return True

        except Exception as e:
            LOGGER.error(f"Failed to initialize streamrip config: {e}")
            LOGGER.warning("Streamrip will be disabled due to configuration errors")
            # Disable streamrip if initialization fails
            from config_manager import Config

            Config.STREAMRIP_ENABLED = False
            self._initialized = False
            self.config = None
            return False

    async def _create_default_config_file(self):
        """Create a default streamrip config file manually"""
        default_config = """
[session]
[session.downloads]
folder = "/usr/src/app/downloads/"
concurrency = 4

[session.qobuz]
quality = 3
email_or_userid = ""
password_or_token = ""
use_auth_token = false

[session.tidal]
quality = 3
username = ""
password = ""
user_id = ""
country_code = ""
access_token = ""
refresh_token = ""
token_expiry = ""

[session.deezer]
quality = 2
arl = ""

[session.soundcloud]
quality = 1

[session.youtube]
quality = 0

[session.conversion]
enabled = false
codec = "flac"

[session.database]
downloads_enabled = true
failed_downloads_enabled = true
downloads_path = "~/.config/streamrip/streamrip_downloads.db"
failed_downloads_path = "~/.config/streamrip/streamrip_failed.db"

[session.filepaths]
track_format = "{artist} - {title}"
folder_format = "{artist} - {album}"

[session.artwork]
embed = true
save_artwork = false
embed_size = 1200
saved_max_width = 1200

[session.metadata]
exclude = []
set_playlist_to_album = true
renumber_playlist_tracks = true

[session.misc]
max_search_results = 20
"""

        try:
            import aiofiles

            async with aiofiles.open(self.config_path, "w") as f:
                await f.write(default_config.strip())
            LOGGER.info(f"Created default config file at {self.config_path}")
        except Exception as e:
            LOGGER.error(f"Failed to create default config file: {e}")
            raise

    async def _apply_bot_settings(self):
        """Apply bot configuration settings to streamrip config"""
        if not self.config:
            return

        try:
            from config_manager import Config

            # Download settings - use DOWNLOAD_DIR
            if hasattr(self.config, "session") and hasattr(
                self.config.session, "downloads"
            ):
                self.config.session.downloads.folder = Config.DOWNLOAD_DIR
                self.config.session.downloads.concurrency = (
                    Config.STREAMRIP_CONCURRENT_DOWNLOADS
                )

            # Quality settings for each platform
            if hasattr(self.config, "session"):
                if hasattr(self.config.session, "qobuz"):
                    self.config.session.qobuz.quality = (
                        Config.STREAMRIP_QOBUZ_QUALITY
                    )
                if hasattr(self.config.session, "tidal"):
                    self.config.session.tidal.quality = (
                        Config.STREAMRIP_TIDAL_QUALITY
                    )
                if hasattr(self.config.session, "deezer"):
                    self.config.session.deezer.quality = (
                        Config.STREAMRIP_DEEZER_QUALITY
                    )
                if hasattr(self.config.session, "soundcloud"):
                    self.config.session.soundcloud.quality = (
                        Config.STREAMRIP_SOUNDCLOUD_QUALITY
                    )

            # Authentication settings
            await self._apply_auth_settings()

            # Metadata settings
            if hasattr(self.config, "session") and hasattr(
                self.config.session, "metadata"
            ):
                # Set metadata exclusions
                if Config.STREAMRIP_METADATA_EXCLUDE:
                    self.config.session.metadata.exclude = (
                        Config.STREAMRIP_METADATA_EXCLUDE
                    )

            # File paths
            if hasattr(self.config, "session") and hasattr(
                self.config.session, "filepaths"
            ):
                if Config.STREAMRIP_FILEPATHS_TRACK_FORMAT:
                    self.config.session.filepaths.track_format = (
                        Config.STREAMRIP_FILEPATHS_TRACK_FORMAT
                    )
                if Config.STREAMRIP_FILEPATHS_FOLDER_FORMAT:
                    self.config.session.filepaths.folder_format = (
                        Config.STREAMRIP_FILEPATHS_FOLDER_FORMAT
                    )

            # Artwork settings
            if hasattr(self.config, "session") and hasattr(
                self.config.session, "artwork"
            ):
                self.config.session.artwork.embed = Config.STREAMRIP_EMBED_COVER_ART
                self.config.session.artwork.save_artwork = (
                    Config.STREAMRIP_SAVE_COVER_ART
                )

            # Database settings
            if hasattr(self.config, "session") and hasattr(
                self.config.session, "database"
            ):
                self.config.session.database.downloads_enabled = (
                    Config.STREAMRIP_DATABASE_DOWNLOADS_ENABLED
                )
                self.config.session.database.failed_downloads_enabled = (
                    Config.STREAMRIP_DATABASE_FAILED_DOWNLOADS_ENABLED
                )

            # Conversion settings
            if hasattr(self.config, "session") and hasattr(
                self.config.session, "conversion"
            ):
                self.config.session.conversion.enabled = (
                    Config.STREAMRIP_CONVERSION_ENABLED
                )
                if Config.STREAMRIP_CONVERSION_CODEC:
                    self.config.session.conversion.codec = (
                        Config.STREAMRIP_CONVERSION_CODEC
                    )

        except Exception as e:
            LOGGER.error(f"Error applying bot settings to streamrip config: {e}")

    async def _apply_auth_settings(self):
        """Apply authentication settings"""
        try:
            from config_manager import Config

            # Qobuz authentication
            if hasattr(self.config.session, "qobuz"):
                if Config.STREAMRIP_QOBUZ_EMAIL:
                    self.config.session.qobuz.email_or_userid = (
                        Config.STREAMRIP_QOBUZ_EMAIL
                    )
                if Config.STREAMRIP_QOBUZ_PASSWORD:
                    self.config.session.qobuz.password_or_token = (
                        Config.STREAMRIP_QOBUZ_PASSWORD
                    )

            # Tidal authentication
            if hasattr(self.config.session, "tidal"):
                if Config.STREAMRIP_TIDAL_ACCESS_TOKEN:
                    self.config.session.tidal.access_token = (
                        Config.STREAMRIP_TIDAL_ACCESS_TOKEN
                    )
                if Config.STREAMRIP_TIDAL_REFRESH_TOKEN:
                    self.config.session.tidal.refresh_token = (
                        Config.STREAMRIP_TIDAL_REFRESH_TOKEN
                    )
                if Config.STREAMRIP_TIDAL_USER_ID:
                    self.config.session.tidal.user_id = (
                        Config.STREAMRIP_TIDAL_USER_ID
                    )
                if Config.STREAMRIP_TIDAL_COUNTRY_CODE:
                    self.config.session.tidal.country_code = (
                        Config.STREAMRIP_TIDAL_COUNTRY_CODE
                    )

            # Deezer authentication
            if hasattr(self.config.session, "deezer"):
                if Config.STREAMRIP_DEEZER_ARL:
                    self.config.session.deezer.arl = Config.STREAMRIP_DEEZER_ARL

        except Exception as e:
            LOGGER.error(f"Error applying auth settings: {e}")

    async def save_config(self):
        """Save configuration to file"""
        if not self.config or not self.config_path:
            return

        try:
            self.config.save(str(self.config_path))
            LOGGER.debug(f"Saved streamrip config to {self.config_path}")
        except Exception as e:
            LOGGER.error(f"Failed to save streamrip config: {e}")

    def get_config(self) -> StreamripConfig | None:
        """Get the streamrip configuration"""
        return self.config

    def is_initialized(self) -> bool:
        """Check if configuration is initialized"""
        return self._initialized

    def is_database_enabled(self) -> bool:
        """Check if streamrip database is enabled in bot settings"""
        from config_manager import Config

        return Config.STREAMRIP_ENABLE_DATABASE

    def get_platform_status(self) -> dict[str, bool]:
        """Get simplified platform status"""
        from config_manager import Config

        return {
            "qobuz": bool(
                Config.STREAMRIP_QOBUZ_ENABLED and Config.STREAMRIP_QOBUZ_EMAIL
            ),
            "tidal": bool(
                Config.STREAMRIP_TIDAL_ENABLED
                and Config.STREAMRIP_TIDAL_ACCESS_TOKEN
            ),
            "deezer": bool(
                Config.STREAMRIP_DEEZER_ENABLED and Config.STREAMRIP_DEEZER_ARL
            ),
            "soundcloud": Config.STREAMRIP_SOUNDCLOUD_ENABLED,
            "lastfm": Config.STREAMRIP_LASTFM_ENABLED,
        }


# Global instance
streamrip_config = StreamripConfigHelper()
