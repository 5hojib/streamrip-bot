import asyncio
from time import time
from typing import Any
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

    # Create dummy classes to prevent import errors
    class QobuzClient:
        pass

    class TidalClient:
        pass

    class DeezerClient:
        pass

    class SoundcloudClient:
        pass


class StreamripSearchHandler:
    """Multi-platform search handler for streamrip"""

    # Platform search types
    PLATFORM_SEARCH_TYPES = {
        "qobuz": ("track", "album", "artist", "playlist"),
        "deezer": ("track", "album", "artist", "playlist"),
        "tidal": ("track", "album", "artist", "playlist"),
        "soundcloud": ("track",),
    }

    # Platform emojis
    PLATFORM_EMOJIS = {
        "qobuz": "🟦",
        "tidal": "⚫",
        "deezer": "🟣",
        "soundcloud": "🟠",
    }

    def __init__(
        self,
        listener,
        query: str,
        platform: str | None = None,
        media_type_filter: str | None = None,
        result_limit: int = 20,
    ):
        self.listener = listener
        self.query = query
        self.platform = platform
        self.media_type_filter = media_type_filter
        self.result_limit = result_limit
        self.search_results = {}
        self.current_page = 0
        self.results_per_page = 5
        self._reply_to = None
        self._time = time()
        self._timeout = 300  # 5 minutes for search
        self.event = asyncio.Event()
        self.selected_result = None
        self.clients = {}

    async def initialize_clients(self) -> bool:
        """Initialize streamrip clients for available platforms"""
        if not STREAMRIP_AVAILABLE:
            return False

        from config_manager import Config
        from streamrip_utils.streamrip_config import streamrip_config

        # Initialize streamrip config
        if not await streamrip_config.lazy_initialize():
            return False

        config = streamrip_config.get_config()
        if not config:
            return False

        # Initialize clients based on available credentials
        try:
            # Qobuz
            if (
                Config.STREAMRIP_QOBUZ_ENABLED
                and Config.STREAMRIP_QOBUZ_EMAIL
                and Config.STREAMRIP_QOBUZ_PASSWORD
            ):
                try:
                    self.clients["qobuz"] = QobuzClient(config.session.qobuz)
                    await self.clients["qobuz"].login()
                except Exception as e:
                    LOGGER.warning(f"Failed to initialize Qobuz client: {e}")

            # Tidal
            if (
                Config.STREAMRIP_TIDAL_ENABLED
                and Config.STREAMRIP_TIDAL_ACCESS_TOKEN
            ):
                try:
                    self.clients["tidal"] = TidalClient(config.session.tidal)
                    await self.clients["tidal"].login()
                except Exception as e:
                    LOGGER.warning(f"Failed to initialize Tidal client: {e}")

            # Deezer
            if Config.STREAMRIP_DEEZER_ENABLED and Config.STREAMRIP_DEEZER_ARL:
                try:
                    self.clients["deezer"] = DeezerClient(config.session.deezer)
                    await self.clients["deezer"].login()
                except Exception as e:
                    LOGGER.warning(f"Failed to initialize Deezer client: {e}")

            # SoundCloud
            if Config.STREAMRIP_SOUNDCLOUD_ENABLED:
                try:
                    self.clients["soundcloud"] = SoundcloudClient(
                        config.session.soundcloud
                    )
                    await self.clients["soundcloud"].login()
                except Exception as e:
                    LOGGER.warning(f"Failed to initialize SoundCloud client: {e}")

        except Exception as e:
            LOGGER.error(f"Error initializing streamrip clients: {e}")

        return len(self.clients) > 0

    async def search(self) -> dict[str, Any] | None:
        """Perform multi-platform search"""
        try:
            if not await self.initialize_clients():
                from utils.message_utils import send_message

                await send_message(
                    self.listener.message,
                    f"{self.listener.tag} ❌ <b>No streamrip platforms are configured!</b>\n\n"
                    f"🎵 <b>Available platforms:</b>\n"
                    f"🟦 <code>Qobuz</code> - Hi-Res FLAC\n"
                    f"⚫ <code>Tidal</code> - MQA/Hi-Res\n"
                    f"🟣 <code>Deezer</code> - CD Quality\n"
                    f"🟠 <code>SoundCloud</code> - MP3 320kbps\n\n"
                    f"💡 <i>Configure credentials in bot settings to enable search.</i>",
                )
                return None

            # Send searching message
            from utils.message_utils import send_message, delete_message

            search_msg = await send_message(
                self.listener.message,
                f"{self.listener.tag} 🔍 <b>Searching for:</b> <code>{self.query}</code>\n\n"
                f"🎵 <b>Platforms:</b> {', '.join(self.clients.keys())}\n"
                f"⏳ <i>Please wait...</i>",
            )

            # Perform search on all platforms or specific platform
            if self.platform and self.platform in self.clients:
                await self._search_platform(self.platform)
            else:
                # Search all available platforms
                search_tasks = []
                for platform_name in self.clients:
                    search_tasks.append(self._search_platform(platform_name))

                await asyncio.gather(*search_tasks, return_exceptions=True)

            # Delete searching message
            await delete_message(search_msg)

            # Check if we have results
            total_results = sum(
                len(results) for results in self.search_results.values()
            )

            if total_results == 0:
                await send_message(
                    self.listener.message,
                    f"{self.listener.tag} ❌ <b>No results found for:</b> <code>{self.query}</code>\n\n"
                    f"💡 <i>Try different keywords or check spelling.</i>",
                )
                return None

            # Show search results
            await self._show_search_results()

            # Wait for user selection
            await self._register_handler_and_wait()

            if self.listener.is_cancelled or not self.selected_result:
                return None

            return self.selected_result

        except Exception as e:
            LOGGER.error(f"Search error: {e}")
            return None

    async def _search_platform(self, platform: str):
        """Search on a specific platform"""
        try:
            client = self.clients[platform]
            results = await self._perform_platform_search(client, platform)

            if results:
                # Apply result limit
                limited_results = results[: self.result_limit]
                self.search_results[platform] = limited_results

        except Exception as e:
            LOGGER.error(f"Search failed on {platform}: {e}")

    async def _perform_platform_search(
        self, client, platform: str
    ) -> list[dict[str, Any]]:
        """Perform actual search on platform"""
        results = []

        try:
            # Get search types for this platform
            search_types = self.PLATFORM_SEARCH_TYPES.get(platform, ("track",))

            # Filter by media type if specified
            if self.media_type_filter:
                search_types = (
                    [self.media_type_filter]
                    if self.media_type_filter in search_types
                    else []
                )

            for search_type in search_types:
                try:
                    # Perform search
                    search_response = await client.search(
                        search_type,
                        self.query,
                        limit=self.result_limit,
                    )

                    if search_response:
                        # Extract results based on platform
                        actual_results = self._extract_results_from_response(
                            search_response, platform, search_type
                        )

                        for item in actual_results:
                            result = await self._extract_search_result(
                                item, platform, search_type
                            )
                            if result:
                                results.append(result)

                except Exception as search_error:
                    LOGGER.warning(
                        f"Search type '{search_type}' failed on {platform}: {search_error}"
                    )
                    continue

        except Exception as e:
            LOGGER.error(f"Platform search error for {platform}: {e}")

        return results

    def _extract_results_from_response(
        self, response, platform: str, search_type: str
    ):
        """Extract results from platform-specific response format"""
        # This would need to be implemented based on actual streamrip API
        # For now, return the response as-is
        if hasattr(response, "items"):
            return response.items
        elif isinstance(response, list):
            return response
        else:
            return [response]

    async def _extract_search_result(
        self, item, platform: str, search_type: str
    ) -> dict[str, Any] | None:
        """Extract search result metadata"""
        try:
            result = {
                "platform": platform,
                "type": search_type,
                "id": getattr(item, "id", "unknown"),
                "title": getattr(item, "title", "Unknown Title"),
                "artist": getattr(item, "artist", "Unknown Artist"),
                "album": getattr(item, "album", "")
                if search_type != "album"
                else getattr(item, "title", ""),
                "duration": getattr(item, "duration", 0),
                "url": f"{platform}:{search_type}:{getattr(item, 'id', 'unknown')}",
            }

            # Add platform-specific metadata
            if hasattr(item, "release_date"):
                result["year"] = getattr(item, "release_date", "")
            if hasattr(item, "track_count"):
                result["track_count"] = getattr(item, "track_count", 0)

            return result

        except Exception as e:
            LOGGER.error(f"Error extracting result metadata: {e}")
            return None

    async def _show_search_results(self):
        """Show search results with pagination"""
        # This would implement the UI for showing search results
        # For now, just log the results
        total_results = sum(len(results) for results in self.search_results.values())
        LOGGER.info(
            f"Found {total_results} results across {len(self.search_results)} platforms"
        )

    async def _register_handler_and_wait(self):
        """Register callback handler and wait for user selection"""
        # This would implement the callback handling
        # For now, just wait for timeout
        try:
            await asyncio.wait_for(self.event.wait(), timeout=self._timeout)
        except TimeoutError:
            LOGGER.warning("Search selection timed out")

    def _format_duration(self, duration: int) -> str:
        """Format duration in seconds to MM:SS"""
        if not duration:
            return "Unknown"

        minutes = duration // 60
        seconds = duration % 60
        return f"{minutes}:{seconds:02d}"


async def search_music(
    listener,
    query: str,
    platform: str | None = None,
    media_type_filter: str | None = None,
    result_limit: int = 20,
) -> dict[str, Any] | None:
    """Search for music across platforms"""
    search_handler = StreamripSearchHandler(
        listener, query, platform, media_type_filter, result_limit
    )
    return await search_handler.search()


async def search_music_auto_first(
    listener,
    query: str,
    platform: str | None = None,
    media_type_filter: str | None = None,
) -> dict[str, Any] | None:
    """Search for music and automatically return first result"""
    search_handler = StreamripSearchHandler(
        listener, query, platform, media_type_filter, 1
    )

    # Perform search without UI
    if not await search_handler.initialize_clients():
        return None

    # Search all platforms or specific platform
    if search_handler.platform and search_handler.platform in search_handler.clients:
        await search_handler._search_platform(search_handler.platform)
    else:
        search_tasks = []
        for platform_name in search_handler.clients:
            search_tasks.append(search_handler._search_platform(platform_name))
        await asyncio.gather(*search_tasks, return_exceptions=True)

    # Return first result
    for platform_results in search_handler.search_results.values():
        if platform_results:
            return platform_results[0]

    return None
