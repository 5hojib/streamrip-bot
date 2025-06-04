import asyncio
import os
from logging import getLogger

from config_manager import Config
from utils.bot_utils import arg_parser, is_authorized, get_user_id
from utils.message_utils import send_message, auto_delete_message
from listeners.streamrip_listener import StreamripListener
from download.streamrip_download import add_streamrip_download
from streamrip_utils.url_parser import (
    is_file_input,
    is_lastfm_url,
    is_streamrip_url,
    parse_file_content,
    parse_streamrip_url,
)
from streamrip_utils.search_handler import search_music

LOGGER = getLogger(__name__)


class StreamripCommands:
    """Streamrip download commands"""

    @staticmethod
    def _get_streamrip_args():
        """Get streamrip-specific argument definitions"""
        return {
            # Streamrip specific flags
            "-q": "",  # Quality level
            "-quality": "",  # Quality level (alias)
            "-c": "",  # Codec
            "-codec": "",  # Codec (alias)
            "-f": False,  # Force run
            "-fd": False,  # Force download
            # Standard flags
            "-n": "",  # Custom name
            "link": "",
        }

    @staticmethod
    async def _process_streamrip_download(message, is_leech=False):
        """Process streamrip download command"""
        try:
            # Check if streamrip is enabled
            if not Config.STREAMRIP_ENABLED:
                reply = await send_message(message, "❌ Streamrip downloads are disabled!")
                await auto_delete_message(reply, time=300)
                return

            # Check authorization
            user_id = get_user_id(message)
            if not is_authorized(user_id):
                reply = await send_message(message, "❌ You are not authorized to use this bot!")
                await auto_delete_message(reply, time=300)
                return

            # Get command text
            text = message.text.split(maxsplit=1)
            if len(text) < 2:
                reply = await send_message(
                    message,
                    "❌ Please provide a streamrip URL or search query!\n\n"
                    "📋 <b>Usage:</b>\n"
                    "• <code>/streamrip https://qobuz.com/album/...</code>\n"
                    "• <code>/streamrip search query</code>\n"
                    "• <code>/streamrip -q 3 -c flac https://...</code>\n\n"
                    "🎵 <b>Supported platforms:</b>\n"
                    "🟦 Qobuz • ⚫ Tidal • 🟣 Deezer • 🟠 SoundCloud"
                )
                await auto_delete_message(reply, time=300)
                return

            # Parse arguments
            args = arg_parser(text[1], " ")
            
            # Extract link from args
            link = args.get("link", "")
            if not link:
                # Try to find URL in the text
                words = text[1].split()
                for word in words:
                    if await is_streamrip_url(word) or is_lastfm_url(word):
                        link = word
                        break
                
                # If no URL found, treat as search query
                if not link:
                    search_query = text[1]
                    # Remove flags from search query
                    for flag in ["-q", "-quality", "-c", "-codec", "-f", "-fd", "-n"]:
                        if flag in search_query:
                            parts = search_query.split()
                            filtered_parts = []
                            skip_next = False
                            for i, part in enumerate(parts):
                                if skip_next:
                                    skip_next = False
                                    continue
                                if part == flag:
                                    skip_next = True
                                    continue
                                if not part.startswith("-"):
                                    filtered_parts.append(part)
                            search_query = " ".join(filtered_parts)
                    
                    if search_query.strip():
                        await StreamripCommands._handle_search(message, search_query.strip(), is_leech, args)
                    else:
                        reply = await send_message(message, "❌ Please provide a URL or search query!")
                        await auto_delete_message(reply, time=300)
                    return

            # Handle file input
            if is_file_input(link):
                await StreamripCommands._handle_file_input(message, link, is_leech, args)
                return

            # Handle single URL
            await StreamripCommands._handle_single_url(message, link, is_leech, args)

        except Exception as e:
            LOGGER.error(f"Error processing streamrip command: {e}")
            reply = await send_message(message, f"❌ Error: {str(e)}")
            await auto_delete_message(reply, time=300)

    @staticmethod
    async def _handle_search(message, query, is_leech, args):
        """Handle search functionality"""
        try:
            # Create listener
            listener = StreamripListener(message, isLeech=is_leech)
            
            # Set custom name if provided
            if args.get("-n"):
                listener.name = args.get("-n")

            # Perform search
            result = await search_music(listener, query)
            
            if result:
                # Extract quality and codec from args
                quality = None
                codec = None
                
                if args.get("-q") or args.get("-quality"):
                    try:
                        quality = int(args.get("-q") or args.get("-quality"))
                    except ValueError:
                        pass
                
                if args.get("-c") or args.get("-codec"):
                    codec = args.get("-c") or args.get("-codec")

                # Start download with search result
                url = result.get("url")
                if url:
                    await StreamripCommands._handle_single_url(message, url, is_leech, args)

        except Exception as e:
            LOGGER.error(f"Error in search handler: {e}")
            reply = await send_message(message, f"❌ Search failed: {str(e)}")
            await auto_delete_message(reply, time=300)

    @staticmethod
    async def _handle_file_input(message, file_content, is_leech, args):
        """Handle file input with multiple URLs"""
        try:
            # Parse file content
            urls = await parse_file_content(file_content)
            
            if not urls:
                reply = await send_message(message, "❌ No valid URLs found in file!")
                await auto_delete_message(reply, time=300)
                return

            # Process each URL
            for i, url in enumerate(urls):
                try:
                    await StreamripCommands._handle_single_url(message, url, is_leech, args)
                    
                    # Add delay between downloads to avoid overwhelming
                    if i < len(urls) - 1:
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    LOGGER.error(f"Error processing URL {url}: {e}")
                    continue

        except Exception as e:
            LOGGER.error(f"Error handling file input: {e}")
            reply = await send_message(message, f"❌ File processing failed: {str(e)}")
            await auto_delete_message(reply, time=300)

    @staticmethod
    async def _handle_single_url(message, url, is_leech, args):
        """Handle single URL download"""
        try:
            # Validate URL
            parsed = await parse_streamrip_url(url)
            if not parsed:
                reply = await send_message(message, f"❌ Invalid URL: {url}")
                await auto_delete_message(reply, time=300)
                return

            platform, media_type, media_id = parsed

            # Create listener
            listener = StreamripListener(message, isLeech=is_leech)
            
            # Set custom name if provided
            if args.get("-n"):
                listener.name = args.get("-n")

            # Extract quality and codec from args
            quality = None
            codec = None
            force = args.get("-f", False) or args.get("-fd", False)
            
            if args.get("-q") or args.get("-quality"):
                try:
                    quality = int(args.get("-q") or args.get("-quality"))
                except ValueError:
                    pass
            
            if args.get("-c") or args.get("-codec"):
                codec = args.get("-c") or args.get("-codec")

            # Start download
            await add_streamrip_download(listener, url, quality, codec, force)

        except Exception as e:
            LOGGER.error(f"Error handling single URL: {e}")
            reply = await send_message(message, f"❌ Download failed: {str(e)}")
            await auto_delete_message(reply, time=300)

    @staticmethod
    async def streamrip_mirror(_, message):
        """Handle streamrip mirror command"""
        await StreamripCommands._process_streamrip_download(message, is_leech=False)

    @staticmethod
    async def streamrip_leech(_, message):
        """Handle streamrip leech command"""
        await StreamripCommands._process_streamrip_download(message, is_leech=True)

    @staticmethod
    async def streamrip_search(_, message):
        """Handle streamrip search command"""
        try:
            # Get search query
            text = message.text.split(maxsplit=1)
            if len(text) < 2:
                reply = await send_message(
                    message,
                    "❌ Please provide a search query!\n\n"
                    "📋 <b>Usage:</b>\n"
                    "• <code>/streamripsearch artist name</code>\n"
                    "• <code>/streamripsearch album title</code>\n"
                    "• <code>/streamripsearch track name</code>"
                )
                await auto_delete_message(reply, time=300)
                return

            query = text[1]
            
            # Handle search without download
            # Create temporary listener for search
            listener = StreamripListener(message, isLeech=False)
            
            # Perform search
            result = await search_music(listener, query)
            
            if result:
                reply = await send_message(
                    message,
                    f"🎵 <b>Search completed!</b>\n"
                    f"📊 <b>Found:</b> {result.get('title', 'Unknown')}\n"
                    f"🎤 <b>Artist:</b> {result.get('artist', 'Unknown')}\n"
                    f"🎯 <b>Platform:</b> {result.get('platform', 'Unknown').title()}\n\n"
                    f"🔗 <b>URL:</b> <code>{result.get('url', '')}</code>"
                )
            else:
                reply = await send_message(message, f"❌ No results found for: {query}")
            
            await auto_delete_message(reply, time=300)

        except Exception as e:
            LOGGER.error(f"Error in search command: {e}")
            reply = await send_message(message, f"❌ Search failed: {str(e)}")
            await auto_delete_message(reply, time=300)
