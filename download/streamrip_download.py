import asyncio
import os
import subprocess
import time
from pathlib import Path
from logging import getLogger

LOGGER = getLogger(__name__)

try:
    from streamrip.client import (
        DeezerClient,
        QobuzClient,
        SoundcloudClient,
        TidalClient,
    )

    STREAMRIP_AVAILABLE = True
except ImportError:
    STREAMRIP_AVAILABLE = False


class StreamripDownloadHelper:
    """Helper class for streamrip downloads"""

    def __init__(
        self,
        listener,
        url: str,
        quality: int | None = None,
        codec: str | None = None,
    ):
        self.listener = listener
        self.url = url
        self.quality = quality
        self.codec = codec
        self.download_path = None
        self.current_track = None
        self._cancelled = False
        self._start_time = time.time()

    async def download(self):
        """Start the download process"""
        try:
            from config_manager import Config
            from streamrip_utils.streamrip_config import streamrip_config
            from streamrip_utils.url_parser import parse_streamrip_url

            # Initialize streamrip config
            if not await streamrip_config.lazy_initialize():
                raise Exception("Failed to initialize streamrip configuration")

            # Parse URL to get platform and media info
            parsed = await parse_streamrip_url(self.url)
            if not parsed:
                raise Exception("Invalid streamrip URL")

            platform, media_type, media_id = parsed

            # Set download path
            self.download_path = (
                Path(Config.DOWNLOAD_DIR) / f"streamrip_{self.listener.mid}"
            )
            self.download_path.mkdir(parents=True, exist_ok=True)

            # Prepare streamrip command
            cmd = ["rip", "url", self.url]

            # Add quality if specified
            if self.quality is not None:
                cmd.extend(["--quality", str(self.quality)])

            # Add codec if specified
            if self.codec:
                cmd.extend(["--codec", self.codec])

            # Add output directory
            cmd.extend(["--directory", str(self.download_path)])

            # Add no-db flag if database is disabled
            if not streamrip_config.is_database_enabled():
                cmd.append("--no-db")

            LOGGER.info(f"Starting streamrip download: {' '.join(cmd)}")

            # Run streamrip command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.download_path),
            )

            # Monitor the process
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Streamrip download failed: {error_msg}")

            # Check if files were downloaded
            downloaded_files = list(self.download_path.rglob("*"))
            audio_files = [
                f
                for f in downloaded_files
                if f.suffix.lower() in [".flac", ".mp3", ".m4a", ".ogg", ".opus"]
            ]

            if not audio_files:
                raise Exception("No audio files were downloaded")

            LOGGER.info(f"Successfully downloaded {len(audio_files)} files")
            return True

        except Exception as e:
            LOGGER.error(f"Download error: {e}")
            raise

    def cancel(self):
        """Cancel the download"""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Check if download is cancelled"""
        return self._cancelled

    def get_progress(self) -> dict:
        """Get download progress"""
        return {
            "status": "downloading" if not self._cancelled else "cancelled",
            "current_track": self.current_track or "Unknown",
            "elapsed_time": time.time() - self._start_time,
        }


async def add_streamrip_download(
    listener,
    url: str,
    quality: int | None = None,
    codec: str | None = None,
    force: bool = False,
):
    """Add streamrip download to queue"""
    if not STREAMRIP_AVAILABLE:
        from utils.message_utils import send_status_message

        await send_status_message(listener.message, "❌ Streamrip is not available!")
        return

    # Check if streamrip is enabled
    from config_manager import Config

    if not Config.STREAMRIP_ENABLED:
        from utils.message_utils import send_status_message

        await send_status_message(
            listener.message, "❌ Streamrip downloads are disabled!"
        )
        return

    # Parse URL to validate
    from streamrip_utils.url_parser import is_streamrip_url, parse_streamrip_url

    if not await is_streamrip_url(url):
        from utils.message_utils import send_status_message

        await send_status_message(listener.message, "❌ Invalid streamrip URL!")
        return

    try:
        # Parse URL to get platform info
        parsed = await parse_streamrip_url(url)
        if not parsed:
            from utils.message_utils import send_status_message

            await send_status_message(listener.message, "❌ Failed to parse URL!")
            return

        platform, media_type, media_id = parsed

        # Check if platform is enabled and configured
        from streamrip_utils.streamrip_config import streamrip_config

        platform_status = streamrip_config.get_platform_status()

        if not platform_status.get(platform, False):
            from utils.message_utils import send_status_message

            await send_status_message(
                listener.message,
                f"❌ {platform.title()} is not configured! Please add credentials in bot settings.",
            )
            return

        # Show quality selector if not specified
        if quality is None or codec is None:
            from streamrip_utils.quality_selector import show_quality_selector

            selection = await show_quality_selector(listener, platform, media_type)
            if not selection:
                return  # User cancelled or timeout

            quality = selection["quality"]
            codec = selection["codec"]

        # Create download helper
        download_helper = StreamripDownloadHelper(listener, url, quality, codec)

        # Add to task dictionary
        from status.streamrip_status import StreamripDownloadStatus

        # Create status object
        status = StreamripDownloadStatus(listener, download_helper)

        # Add to global task dictionary (you would implement this)
        # task_dict[listener.mid] = status

        # Start download
        from utils.message_utils import send_status_message

        await send_status_message(
            listener.message,
            f"🎵 <b>Starting {platform.title()} download...</b>\n"
            f"📁 <b>Type:</b> {media_type.title()}\n"
            f"📊 <b>Quality:</b> {quality}\n"
            f"🎵 <b>Format:</b> {codec.upper()}",
        )

        # Start the actual download
        await download_helper.download()

        # Handle upload after download
        await listener.on_download_complete()

    except Exception as e:
        LOGGER.error(f"Error adding streamrip download: {e}")
        from utils.message_utils import send_status_message

        await send_status_message(
            listener.message, f"❌ <b>Download failed:</b> {str(e)}"
        )


async def extract_streamrip_metadata_name(
    url: str, platform: str, media_type: str
) -> str | None:
    """Extract metadata name from streamrip URL"""
    try:
        # This would use streamrip API to get metadata
        # For now, return a simple name
        from streamrip_utils.url_parser import parse_streamrip_url

        parsed = await parse_streamrip_url(url)
        if not parsed:
            return None

        platform, media_type, media_id = parsed
        return f"{platform}_{media_type}_{media_id}"

    except Exception as e:
        LOGGER.error(f"Error extracting metadata name: {e}")
        return None
