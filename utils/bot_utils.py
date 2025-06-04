import asyncio
import time
from functools import wraps
from logging import getLogger

LOGGER = getLogger(__name__)


def new_task(func):
    """Decorator to run function as a new task"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.create_task(func(*args, **kwargs))

    return wrapper


def arg_parser(text, separator=" "):
    """Parse arguments from text"""
    if not text:
        return {}

    args = {}
    parts = text.split(separator)

    for i, part in enumerate(parts):
        if part.startswith("-"):
            # Flag with value
            if i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                args[part] = parts[i + 1]
            else:
                # Boolean flag
                args[part] = True

    return args


def get_readable_time(seconds):
    """Convert seconds to readable time format"""
    if seconds <= 0:
        return "0s"

    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]

    result = []
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result.append(f"{int(period_value)}{period_name}")

    return " ".join(result)


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


def is_authorized(user_id, authorized_chats=None, sudo_users=None):
    """Check if user is authorized"""
    from config_manager import Config

    # Owner is always authorized
    if user_id == Config.OWNER_ID:
        return True

    # Check sudo users
    if sudo_users or Config.SUDO_USERS:
        sudo_list = sudo_users or Config.SUDO_USERS.split()
        if str(user_id) in sudo_list:
            return True

    return True  # For standalone bot, allow all users by default


def get_user_id(message):
    """Get user ID from message"""
    return message.from_user.id


def get_user_tag(message):
    """Get user tag for mentions"""
    user = message.from_user
    if user.username:
        return f"@{user.username}"
    else:
        return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"


class TaskConfig:
    """Base configuration for tasks"""

    def __init__(self):
        self.is_leech = False
        self.name = ""
        self.up_dest = ""
        self.rc_flags = ""
        self.user_id = None
        self.message = None
        self.tag = ""
        self.mid = ""
        self.is_cancelled = False


def generate_task_id():
    """Generate a unique task ID"""
    return str(int(time.time() * 1000))