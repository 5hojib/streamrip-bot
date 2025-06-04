import time
from logging import getLogger
from pathlib import Path

LOGGER = getLogger(__name__)


class StreamripListener:
    """Streamrip download listener"""

    def __init__(self, message, isLeech=False, tag=None, user_id=None):
        # Set required attributes
        self.message = message
        self.is_leech = isLeech
        self.isLeech = isLeech  # Alias for compatibility

        # User information
        self.user_id = user_id or message.from_user.id
        self.tag = tag or self._get_user_tag()

        # Task information
        self.mid = self._generate_task_id()
        self.name = ""
        self.dir = ""

        # Upload settings
        self.up_dest = ""
        self.rc_flags = ""

        # Status
        self.is_cancelled = False
        self._start_time = time.time()

        # Initialize download directory
        self._setup_download_dir()

    def _get_user_tag(self):
        """Get user tag for mentions"""
        user = self.message.from_user
        if user.username:
            return f"@{user.username}"
        else:
            return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    def _generate_task_id(self):
        """Generate a unique task ID"""
        return str(int(time.time() * 1000))

    def _setup_download_dir(self):
        """Setup download directory"""
        from config_manager import Config

        base_dir = Path(Config.DOWNLOAD_DIR)
        self.dir = base_dir / f"streamrip_{self.mid}"
        self.dir.mkdir(parents=True, exist_ok=True)

    async def on_download_start(self):
        """Called when download starts"""
        LOGGER.info(f"Starting streamrip download for user {self.user_id}")

    async def on_download_progress(self, current_track=None):
        """Called during download progress"""
        if current_track:
            self.name = current_track

    async def on_download_complete(self):
        """Called when download completes"""
        try:
            LOGGER.info(f"Streamrip download completed: {self.mid}")

            # Check if files exist
            if not self.dir.exists() or not any(self.dir.iterdir()):
                raise Exception("No files downloaded")

            # Handle upload based on leech/mirror mode
            if self.is_leech:
                await self._handle_leech_upload()
            else:
                await self._handle_mirror_upload()

        except Exception as e:
            LOGGER.error(f"Error in download complete handler: {e}")
            await self.on_download_error(str(e))

    async def on_download_error(self, error_message):
        """Called when download fails"""
        try:
            from utils.message_utils import send_message

            await send_message(
                self.message,
                f"{self.tag} ❌ <b>Download failed:</b>\n<code>{error_message}</code>",
            )

            # Cleanup
            await self._cleanup()

        except Exception as e:
            LOGGER.error(f"Error in download error handler: {e}")

    async def _handle_leech_upload(self):
        """Handle leech upload (send files to Telegram)"""
        try:
            from utils.message_utils import send_message

            # Get all audio files
            audio_files = list(self.dir.rglob("*"))
            audio_files = [
                f
                for f in audio_files
                if f.suffix.lower() in [".flac", ".mp3", ".m4a", ".ogg", ".opus"]
            ]

            if not audio_files:
                raise Exception("No audio files found")

            # Send files to Telegram
            await send_message(
                self.message,
                f"{self.tag} 📤 <b>Uploading {len(audio_files)} files...</b>",
            )

            for audio_file in audio_files:
                try:
                    # Send audio file
                    with open(audio_file, "rb") as f:
                        await self.message.reply_audio(
                            f,
                            caption=f"🎵 {audio_file.name}",
                            title=audio_file.stem,
                        )
                except Exception as e:
                    LOGGER.error(f"Error uploading file {audio_file}: {e}")

            # Send completion message
            await send_message(
                self.message,
                f"{self.tag} ✅ <b>Upload completed!</b>\n"
                f"📁 <b>Files:</b> {len(audio_files)}\n"
                f"⏱️ <b>Total time:</b> {self._get_elapsed_time()}",
            )

            # Cleanup
            await self._cleanup()

        except Exception as e:
            LOGGER.error(f"Error in leech upload: {e}")
            await self.on_download_error(f"Upload failed: {str(e)}")

    async def _handle_mirror_upload(self):
        """Handle mirror upload (upload to cloud storage)"""
        try:
            from utils.message_utils import send_message

            # For now, just send a message that mirror is not implemented
            await send_message(
                self.message,
                f"{self.tag} ℹ️ <b>Mirror upload not implemented yet.</b>\n"
                f"📁 <b>Files saved to:</b> <code>{self.dir}</code>\n"
                f"⏱️ <b>Total time:</b> {self._get_elapsed_time()}",
            )

            # Cleanup
            await self._cleanup()

        except Exception as e:
            LOGGER.error(f"Error in mirror upload: {e}")
            await self.on_download_error(f"Mirror upload failed: {str(e)}")

    async def _cleanup(self):
        """Cleanup download directory"""
        try:
            import shutil

            if self.dir.exists():
                shutil.rmtree(self.dir)
                LOGGER.info(f"Cleaned up download directory: {self.dir}")

        except Exception as e:
            LOGGER.error(f"Error cleaning up directory {self.dir}: {e}")

    def _get_elapsed_time(self):
        """Get elapsed time in readable format"""
        elapsed = time.time() - self._start_time

        if elapsed < 60:
            return f"{int(elapsed)}s"
        elif elapsed < 3600:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            return f"{hours}h {minutes}m"

    def cancel(self):
        """Cancel the download"""
        self.is_cancelled = True
        LOGGER.info(f"Cancelled streamrip download: {self.mid}")

    def get_status(self):
        """Get current status"""
        if self.is_cancelled:
            return "Cancelled"
        return "Downloading"

    def get_progress_info(self):
        """Get progress information"""
        return {
            "status": self.get_status(),
            "name": self.name or "Streamrip Download",
            "elapsed_time": self._get_elapsed_time(),
            "user_tag": self.tag,
        }
