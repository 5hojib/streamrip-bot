"""
Settings UI for Streamrip Bot Configuration Management
Provides interactive interface for managing bot settings
"""

import asyncio
from time import time
from logging import getLogger

LOGGER = getLogger(__name__)

# Global registry for active settings sessions
_active_settings_sessions = {}


def get_active_settings_session(user_id):
    """Get active settings session for a user"""
    return _active_settings_sessions.get(user_id)


def register_settings_session(user_id, session):
    """Register a settings session for a user"""
    _active_settings_sessions[user_id] = session


def unregister_settings_session(user_id):
    """Unregister a settings session for a user"""
    _active_settings_sessions.pop(user_id, None)


class StreamripSettings:
    """Interactive settings manager for streamrip bot configuration"""

    def __init__(self, listener):
        self.listener = listener
        self._reply_to = None
        self._time = time()
        self._timeout = 300  # 5 minutes
        self.event = asyncio.Event()
        self.current_menu = "main"
        self.current_platform = None
        self._changes_made = False

    async def show_settings_menu(self):
        """Show main settings interface"""
        try:
            # Register this settings session
            register_settings_session(self.listener.user_id, self)

            # Show main menu
            await self._show_main_menu()

            # Wait for user interaction
            await self._register_handler_and_wait()

        except Exception as e:
            LOGGER.error(f"Error in settings menu: {e}")
        finally:
            # Cleanup
            unregister_settings_session(self.listener.user_id)

    async def _register_handler_and_wait(self):
        """Register callback handler and wait for user interaction"""
        try:
            await asyncio.wait_for(self.event.wait(), timeout=self._timeout)
        except TimeoutError:
            LOGGER.warning("Settings session timed out")
            from utils.message_utils import send_message, delete_message
            
            timeout_msg = await send_message(
                self.listener.message,
                f"{self.listener.tag} ⏰ <b>Settings session timed out.</b>"
            )

            # Delete the settings menu
            if self._reply_to and hasattr(self._reply_to, "delete"):
                await delete_message(self._reply_to)

    async def handle_callback(self, query):
        """Handle callback query from settings interface"""
        try:
            # Validate user
            if query.from_user.id != self.listener.user_id:
                await query.answer("❌ Not authorized")
                return

            # Answer callback
            await query.answer()

            # Parse callback data
            data = query.data.split("_")
            if len(data) < 2 or data[0] != "settings":
                return

            action = data[1]

            if action == "main":
                await self._show_main_menu()
            elif action == "platforms":
                await self._show_platforms_menu()
            elif action == "quality":
                await self._show_quality_menu()
            elif action == "download":
                await self._show_download_menu()
            elif action == "platform":
                if len(data) >= 3:
                    self.current_platform = data[2]
                    await self._show_platform_config(data[2])
            elif action == "set":
                if len(data) >= 4:
                    await self._handle_setting_change(data[2], data[3])
            elif action == "toggle":
                if len(data) >= 3:
                    await self._handle_toggle(data[2])
            elif action == "save":
                await self._save_settings()
            elif action == "close":
                await self._close_settings()
            else:
                LOGGER.warning(f"Unknown settings action: {action}")

        except Exception as e:
            LOGGER.error(f"Error handling settings callback: {e}")

    async def _show_main_menu(self):
        """Show main settings menu"""
        from utils.button_build import ButtonMaker
        from utils.message_utils import send_message, edit_message
        from config_manager import Config

        buttons = ButtonMaker()

        # Main menu message
        msg = "<b>⚙️ Streamrip Bot Settings</b>\n\n"
        msg += f"<b>🤖 Bot Status:</b> {'✅ Active' if Config.STREAMRIP_ENABLED else '❌ Disabled'}\n"
        msg += f"<b>👤 Owner:</b> <code>{Config.OWNER_ID}</code>\n"
        msg += f"<b>📁 Download Dir:</b> <code>{Config.DOWNLOAD_DIR}</code>\n\n"

        # Platform status
        from streamrip_utils.streamrip_config import streamrip_config
        platform_status = streamrip_config.get_platform_status()
        
        msg += "<b>🎵 Platform Status:</b>\n"
        msg += f"🟦 Qobuz: {'✅' if platform_status.get('qobuz') else '❌'}\n"
        msg += f"⚫ Tidal: {'✅' if platform_status.get('tidal') else '❌'}\n"
        msg += f"🟣 Deezer: {'✅' if platform_status.get('deezer') else '❌'}\n"
        msg += f"🟠 SoundCloud: {'✅' if platform_status.get('soundcloud') else '❌'}\n\n"

        # Menu buttons
        buttons.data_button("🎵 Platform Settings", "settings_platforms")
        buttons.data_button("📊 Quality Settings", "settings_quality")
        buttons.data_button("📥 Download Settings", "settings_download")
        buttons.data_button("💾 Save Changes", "settings_save", "footer")
        buttons.data_button("❌ Close", "settings_close", "footer")

        msg += f"<b>⏱️ Session timeout:</b> <code>{self._get_readable_time(self._timeout - (time() - self._time))}</code>"

        # Send or edit message
        if self._reply_to and hasattr(self._reply_to, "edit"):
            await edit_message(self._reply_to, msg, buttons.build_menu(1))
        else:
            self._reply_to = await send_message(
                self.listener.message, msg, buttons.build_menu(1)
            )

    async def _show_platforms_menu(self):
        """Show platform configuration menu"""
        from utils.button_build import ButtonMaker
        from utils.message_utils import edit_message

        buttons = ButtonMaker()

        msg = "<b>🎵 Platform Configuration</b>\n\n"
        msg += "Configure streaming platform credentials:\n\n"

        # Platform buttons
        buttons.data_button("🟦 Qobuz Settings", "settings_platform_qobuz")
        buttons.data_button("⚫ Tidal Settings", "settings_platform_tidal")
        buttons.data_button("🟣 Deezer Settings", "settings_platform_deezer")
        buttons.data_button("🟠 SoundCloud Settings", "settings_platform_soundcloud")

        # Navigation
        buttons.data_button("⬅️ Back", "settings_main", "footer")
        buttons.data_button("❌ Close", "settings_close", "footer")

        await edit_message(self._reply_to, msg, buttons.build_menu(1))

    async def _show_quality_menu(self):
        """Show quality settings menu"""
        from utils.button_build import ButtonMaker
        from utils.message_utils import edit_message
        from config_manager import Config

        buttons = ButtonMaker()

        msg = "<b>📊 Quality Settings</b>\n\n"
        msg += f"<b>Default Quality:</b> <code>{Config.STREAMRIP_DEFAULT_QUALITY}</code>\n"
        msg += f"<b>Default Codec:</b> <code>{Config.STREAMRIP_DEFAULT_CODEC}</code>\n"
        msg += f"<b>Fallback Quality:</b> <code>{Config.STREAMRIP_FALLBACK_QUALITY}</code>\n\n"

        # Quality level buttons
        for quality in range(5):
            quality_names = ["128kbps", "320kbps", "CD", "Hi-Res", "Hi-Res+"]
            current = "✅" if quality == Config.STREAMRIP_DEFAULT_QUALITY else ""
            buttons.data_button(
                f"{current} {quality}: {quality_names[quality]}",
                f"settings_set_quality_{quality}"
            )

        # Codec buttons
        msg += "<b>Available Codecs:</b>\n"
        for codec in Config.STREAMRIP_SUPPORTED_CODECS:
            current = "✅" if codec == Config.STREAMRIP_DEFAULT_CODEC else ""
            buttons.data_button(
                f"{current} {codec.upper()}",
                f"settings_set_codec_{codec}"
            )

        # Navigation
        buttons.data_button("⬅️ Back", "settings_main", "footer")
        buttons.data_button("❌ Close", "settings_close", "footer")

        await edit_message(self._reply_to, msg, buttons.build_menu(2))

    async def _show_download_menu(self):
        """Show download settings menu"""
        from utils.button_build import ButtonMaker
        from utils.message_utils import edit_message
        from config_manager import Config

        buttons = ButtonMaker()

        msg = "<b>📥 Download Settings</b>\n\n"
        msg += f"<b>Download Directory:</b>\n<code>{Config.DOWNLOAD_DIR}</code>\n\n"
        msg += f"<b>Concurrent Downloads:</b> <code>{Config.STREAMRIP_CONCURRENT_DOWNLOADS}</code>\n"
        msg += f"<b>Max Search Results:</b> <code>{Config.STREAMRIP_MAX_SEARCH_RESULTS}</code>\n"
        msg += f"<b>Database Enabled:</b> {'✅' if Config.STREAMRIP_ENABLE_DATABASE else '❌'}\n"
        msg += f"<b>Auto Convert:</b> {'✅' if Config.STREAMRIP_AUTO_CONVERT else '❌'}\n\n"

        # Toggle buttons
        buttons.data_button(
            f"{'✅' if Config.STREAMRIP_ENABLE_DATABASE else '❌'} Database",
            "settings_toggle_database"
        )
        buttons.data_button(
            f"{'✅' if Config.STREAMRIP_AUTO_CONVERT else '❌'} Auto Convert",
            "settings_toggle_convert"
        )

        # Concurrent downloads
        for count in [2, 4, 6, 8]:
            current = "✅" if count == Config.STREAMRIP_CONCURRENT_DOWNLOADS else ""
            buttons.data_button(
                f"{current} {count} Concurrent",
                f"settings_set_concurrent_{count}"
            )

        # Navigation
        buttons.data_button("⬅️ Back", "settings_main", "footer")
        buttons.data_button("❌ Close", "settings_close", "footer")

        await edit_message(self._reply_to, msg, buttons.build_menu(2))

    async def _show_platform_config(self, platform):
        """Show specific platform configuration"""
        from utils.button_build import ButtonMaker
        from utils.message_utils import edit_message
        from config_manager import Config

        buttons = ButtonMaker()

        platform_info = {
            "qobuz": {
                "name": "🟦 Qobuz",
                "email": Config.STREAMRIP_QOBUZ_EMAIL,
                "password": "***" if Config.STREAMRIP_QOBUZ_PASSWORD else "",
                "enabled": Config.STREAMRIP_QOBUZ_ENABLED,
                "quality": Config.STREAMRIP_QOBUZ_QUALITY,
            },
            "tidal": {
                "name": "⚫ Tidal",
                "token": "***" if Config.STREAMRIP_TIDAL_ACCESS_TOKEN else "",
                "enabled": Config.STREAMRIP_TIDAL_ENABLED,
                "quality": Config.STREAMRIP_TIDAL_QUALITY,
            },
            "deezer": {
                "name": "🟣 Deezer",
                "arl": "***" if Config.STREAMRIP_DEEZER_ARL else "",
                "enabled": Config.STREAMRIP_DEEZER_ENABLED,
                "quality": Config.STREAMRIP_DEEZER_QUALITY,
            },
            "soundcloud": {
                "name": "🟠 SoundCloud",
                "enabled": Config.STREAMRIP_SOUNDCLOUD_ENABLED,
                "quality": Config.STREAMRIP_SOUNDCLOUD_QUALITY,
            },
        }

        info = platform_info.get(platform, {})
        msg = f"<b>{info.get('name', platform.title())} Configuration</b>\n\n"

        if platform == "qobuz":
            msg += f"<b>Email:</b> <code>{info.get('email', 'Not set')}</code>\n"
            msg += f"<b>Password:</b> <code>{info.get('password', 'Not set')}</code>\n"
        elif platform == "tidal":
            msg += f"<b>Access Token:</b> <code>{info.get('token', 'Not set')}</code>\n"
        elif platform == "deezer":
            msg += f"<b>ARL Cookie:</b> <code>{info.get('arl', 'Not set')}</code>\n"

        msg += f"<b>Enabled:</b> {'✅' if info.get('enabled') else '❌'}\n"
        msg += f"<b>Quality:</b> <code>{info.get('quality', 0)}</code>\n\n"

        # Toggle enabled/disabled
        buttons.data_button(
            f"{'❌ Disable' if info.get('enabled') else '✅ Enable'}",
            f"settings_toggle_{platform}"
        )

        # Quality settings
        max_quality = 4 if platform == "qobuz" else 3 if platform in ["tidal", "deezer"] else 1
        for q in range(max_quality + 1):
            current = "✅" if q == info.get('quality') else ""
            buttons.data_button(
                f"{current} Quality {q}",
                f"settings_set_{platform}_quality_{q}"
            )

        # Navigation
        buttons.data_button("⬅️ Back to Platforms", "settings_platforms", "footer")
        buttons.data_button("❌ Close", "settings_close", "footer")

        await edit_message(self._reply_to, msg, buttons.build_menu(2))

    async def _handle_setting_change(self, setting_type, value):
        """Handle setting change"""
        from config_manager import Config

        try:
            if setting_type == "quality":
                Config.STREAMRIP_DEFAULT_QUALITY = int(value)
                self._changes_made = True
                await self._show_quality_menu()
            elif setting_type == "codec":
                Config.STREAMRIP_DEFAULT_CODEC = value
                self._changes_made = True
                await self._show_quality_menu()
            elif setting_type == "concurrent":
                Config.STREAMRIP_CONCURRENT_DOWNLOADS = int(value)
                self._changes_made = True
                await self._show_download_menu()
            elif "_quality_" in setting_type:
                platform, _, quality = setting_type.partition("_quality_")
                quality = int(quality)
                
                if platform == "qobuz":
                    Config.STREAMRIP_QOBUZ_QUALITY = quality
                elif platform == "tidal":
                    Config.STREAMRIP_TIDAL_QUALITY = quality
                elif platform == "deezer":
                    Config.STREAMRIP_DEEZER_QUALITY = quality
                elif platform == "soundcloud":
                    Config.STREAMRIP_SOUNDCLOUD_QUALITY = quality
                
                self._changes_made = True
                await self._show_platform_config(platform)

        except Exception as e:
            LOGGER.error(f"Error handling setting change: {e}")

    async def _handle_toggle(self, setting):
        """Handle toggle setting"""
        from config_manager import Config

        try:
            if setting == "database":
                Config.STREAMRIP_ENABLE_DATABASE = not Config.STREAMRIP_ENABLE_DATABASE
                self._changes_made = True
                await self._show_download_menu()
            elif setting == "convert":
                Config.STREAMRIP_AUTO_CONVERT = not Config.STREAMRIP_AUTO_CONVERT
                self._changes_made = True
                await self._show_download_menu()
            elif setting == "qobuz":
                Config.STREAMRIP_QOBUZ_ENABLED = not Config.STREAMRIP_QOBUZ_ENABLED
                self._changes_made = True
                await self._show_platform_config("qobuz")
            elif setting == "tidal":
                Config.STREAMRIP_TIDAL_ENABLED = not Config.STREAMRIP_TIDAL_ENABLED
                self._changes_made = True
                await self._show_platform_config("tidal")
            elif setting == "deezer":
                Config.STREAMRIP_DEEZER_ENABLED = not Config.STREAMRIP_DEEZER_ENABLED
                self._changes_made = True
                await self._show_platform_config("deezer")
            elif setting == "soundcloud":
                Config.STREAMRIP_SOUNDCLOUD_ENABLED = not Config.STREAMRIP_SOUNDCLOUD_ENABLED
                self._changes_made = True
                await self._show_platform_config("soundcloud")

        except Exception as e:
            LOGGER.error(f"Error handling toggle: {e}")

    async def _save_settings(self):
        """Save current settings"""
        from utils.message_utils import send_message, delete_message

        try:
            # Here you would implement actual saving to config file or database
            # For now, just show confirmation
            
            save_msg = await send_message(
                self.listener.message,
                f"{self.listener.tag} ✅ <b>Settings saved successfully!</b>\n\n"
                f"💡 <i>Note: Some changes may require bot restart to take effect.</i>"
            )

            # Delete settings menu
            if self._reply_to and hasattr(self._reply_to, "delete"):
                await delete_message(self._reply_to)

            self.event.set()

        except Exception as e:
            LOGGER.error(f"Error saving settings: {e}")

    async def _close_settings(self):
        """Close settings menu"""
        from utils.message_utils import delete_message

        try:
            # Delete settings menu
            if self._reply_to and hasattr(self._reply_to, "delete"):
                await delete_message(self._reply_to)

            if self._changes_made:
                from utils.message_utils import send_message
                await send_message(
                    self.listener.message,
                    f"{self.listener.tag} ⚠️ <b>Settings closed with unsaved changes!</b>\n\n"
                    f"💡 <i>Use /settings again to save your changes.</i>"
                )

            self.event.set()

        except Exception as e:
            LOGGER.error(f"Error closing settings: {e}")

    def _get_readable_time(self, seconds):
        """Convert seconds to readable time format"""
        if seconds <= 0:
            return "0s"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"


async def show_settings_menu(listener):
    """Show settings menu for a user"""
    settings = StreamripSettings(listener)
    await settings.show_settings_menu()


# Callback handler for settings
async def handle_settings_callback(_, query):
    """Handle settings callback queries"""
    user_id = query.from_user.id
    
    # Check for active settings session
    settings_session = get_active_settings_session(user_id)
    if settings_session and query.data.startswith("settings_"):
        await settings_session.handle_callback(query)
        return True
    
    return False
