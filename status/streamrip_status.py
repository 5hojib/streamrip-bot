import time
from logging import getLogger

LOGGER = getLogger(__name__)


class MirrorStatus:
    """Status constants for downloads"""
    STATUS_DOWNLOAD = "Downloading"
    STATUS_UPLOAD = "Uploading"
    STATUS_QUEUEDL = "Queued Download"
    STATUS_QUEUEUP = "Queued Upload"
    STATUS_PAUSED = "Paused"
    STATUS_ARCHIVING = "Archiving"
    STATUS_EXTRACTING = "Extracting"
    STATUS_CLONING = "Cloning"
    STATUS_SEEDING = "Seeding"


class StreamripDownloadStatus:
    """Status class for streamrip downloads following standard bot pattern"""

    def __init__(self, listener, download_helper, queued=False):
        self.listener = listener
        self.download_helper = download_helper
        self.queued = queued
        self._start_time = time.time()
        self.tool = "streamrip"  # Required by status system

    def gid(self):
        """Get unique identifier"""
        return self.listener.mid

    def status(self):
        """Get current status"""
        if self.listener.is_cancelled:
            return MirrorStatus.STATUS_PAUSED
        if self.queued:
            return MirrorStatus.STATUS_QUEUEDL
        return MirrorStatus.STATUS_DOWNLOAD

    def name(self):
        """Get download name"""
        if (
            hasattr(self.download_helper, "_current_track")
            and self.download_helper._current_track
        ):
            return self.download_helper._current_track
        if (
            hasattr(self.download_helper, "current_track")
            and self.download_helper.current_track
        ):
            return self.download_helper.current_track
        return self.listener.name or "Streamrip Download"

    def size(self):
        """Get total size"""
        return "N/A"

    def processed_bytes(self):
        """Get processed bytes"""
        return "N/A"

    def speed(self):
        """Get download speed"""
        return "N/A"

    def eta(self):
        """Get estimated time of arrival"""
        return "-"

    def progress(self):
        """Get download progress"""
        return "N/A"

    def task(self):
        """Get task object (standard method)"""
        return self

    def elapsed_time(self):
        """Get elapsed time"""
        return time.time() - self._start_time

    def engine(self):
        """Get download engine"""
        return "Streamrip"

    def download_speed(self):
        """Get download speed (alias for speed)"""
        return self.speed()

    def upload_speed(self):
        """Get upload speed"""
        return "N/A"

    def seeders_leechers(self):
        """Get seeders/leechers info"""
        return "N/A"

    def ratio(self):
        """Get ratio"""
        return "N/A"

    def seeding_time(self):
        """Get seeding time"""
        return "N/A"

    def cancel_download(self):
        """Cancel the download"""
        try:
            self.listener.is_cancelled = True
            if hasattr(self.download_helper, 'cancel'):
                self.download_helper.cancel()
            LOGGER.info(f"Cancelled streamrip download: {self.gid()}")
        except Exception as e:
            LOGGER.error(f"Error cancelling download: {e}")

    def get_readable_status(self):
        """Get human-readable status"""
        status = self.status()
        elapsed = self.elapsed_time()
        
        elapsed_str = self._format_time(elapsed)
        
        if status == MirrorStatus.STATUS_DOWNLOAD:
            return f"📥 Downloading • {elapsed_str}"
        elif status == MirrorStatus.STATUS_QUEUEDL:
            return f"⏳ Queued • {elapsed_str}"
        elif status == MirrorStatus.STATUS_PAUSED:
            return f"⏸️ Cancelled • {elapsed_str}"
        else:
            return f"{status} • {elapsed_str}"

    def _format_time(self, seconds):
        """Format time in seconds to readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def get_progress_bar(self, length=20):
        """Get progress bar (not applicable for streamrip)"""
        return "█" * length  # Full bar since we can't track progress

    def get_status_message(self):
        """Get formatted status message"""
        msg = f"<b>🎵 {self.name()}</b>\n"
        msg += f"<b>📊 Status:</b> {self.get_readable_status()}\n"
        msg += f"<b>🔧 Engine:</b> {self.engine()}\n"
        msg += f"<b>📁 Size:</b> {self.size()}\n"
        msg += f"<b>⚡ Speed:</b> {self.speed()}\n"
        msg += f"<b>⏱️ ETA:</b> {self.eta()}\n"
        msg += f"<b>📈 Progress:</b> {self.progress()}"
        return msg
