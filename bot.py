#!/usr/bin/env python3
"""
Standalone Streamrip Bot
A Telegram bot for downloading high-quality music from streaming platforms
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import only what's needed at module level
from pyrogram import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s [%(module)s:%(lineno)d]',
    handlers=[
        logging.FileHandler('streamrip_bot.log'),
        logging.StreamHandler()
    ]
)

LOGGER = logging.getLogger(__name__)

# Global variables
task_dict = {}
task_dict_lock = asyncio.Lock()
bot = None
user_bot = None


async def main():
    """Main function to start the bot"""
    try:
        # Load configuration
        LOGGER.info("Loading configuration...")
        from config_manager import Config
        Config.load()

        # Initialize Pyrogram clients
        LOGGER.info("Initializing Telegram clients...")

        global bot, user_bot
        
        # Initialize bot client
        bot = Client(
            "streamrip_bot",
            api_id=Config.TELEGRAM_API,
            api_hash=Config.TELEGRAM_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=4,
        )
        
        # Initialize user client if session string is provided
        if Config.USER_SESSION_STRING:
            user_bot = Client(
                "streamrip_user",
                api_id=Config.TELEGRAM_API,
                api_hash=Config.TELEGRAM_HASH,
                session_string=Config.USER_SESSION_STRING,
                workers=2,
            )
        
        # Register handlers
        LOGGER.info("Registering command handlers...")
        register_handlers()
        
        # Start clients
        LOGGER.info("Starting Telegram clients...")
        await bot.start()
        
        if user_bot:
            await user_bot.start()
            LOGGER.info("User client started successfully")
        
        # Initialize streamrip configuration
        LOGGER.info("Initializing streamrip configuration...")
        from streamrip_utils.streamrip_config import streamrip_config
        if await streamrip_config.initialize():
            LOGGER.info("Streamrip configuration initialized successfully")
        else:
            LOGGER.warning("Failed to initialize streamrip configuration")
        
        # Set bot commands
        await set_bot_commands()
        
        # Send startup message
        if Config.LOG_CHAT_ID:
            try:
                await bot.send_message(
                    Config.LOG_CHAT_ID,
                    "🎵 <b>Streamrip Bot Started!</b>\n\n"
                    f"🤖 <b>Bot:</b> @{(await bot.get_me()).username}\n"
                    f"🎧 <b>Streamrip:</b> {'✅ Available' if Config.STREAMRIP_ENABLED else '❌ Disabled'}\n"
                    f"⏰ <b>Started at:</b> {asyncio.get_event_loop().time()}"
                )
            except Exception as e:
                LOGGER.error(f"Failed to send startup message: {e}")
        
        LOGGER.info("🎵 Streamrip Bot started successfully!")
        LOGGER.info(f"Bot username: @{(await bot.get_me()).username}")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Error starting bot: {e}")
        raise
    finally:
        # Cleanup
        if bot:
            await bot.stop()
        if user_bot:
            await user_bot.stop()


def register_handlers():
    """Register command handlers"""
    from pyrogram import filters
    from pyrogram.handlers import MessageHandler, CallbackQueryHandler
    from commands.streamrip_commands import StreamripCommands
    from commands.bot_commands import BotCommands
    from utils.bot_utils import new_task
    
    # Import callback handlers
    from streamrip_utils.quality_selector import get_active_quality_selector
    from settings import handle_settings_callback
    
    # Start command
    async def start_command(_, message):
        from commands.bot_commands import START_TEXT
        from utils.message_utils import send_message
        await send_message(message, START_TEXT)
    
    # Help command
    async def help_command(_, message):
        from commands.bot_commands import HELP_TEXT
        from utils.message_utils import send_message
        await send_message(message, HELP_TEXT)
    
    # Status command
    async def status_command(_, message):
        from utils.message_utils import send_message

        if not task_dict:
            await send_message(message, "📭 <b>No active downloads</b>")
            return

        status_msg = "📊 <b>Active Downloads:</b>\n\n"
        for task_id, task in task_dict.items():
            if hasattr(task, 'get_status_message'):
                status_msg += task.get_status_message() + "\n\n"
            else:
                status_msg += f"🎵 Task {task_id}: Active\n\n"

        await send_message(message, status_msg)

    # Settings command
    async def settings_command(_, message):
        from utils.bot_utils import is_authorized, get_user_id
        from utils.message_utils import send_message
        from listeners.streamrip_listener import StreamripListener
        from settings import show_settings_menu

        # Check authorization
        user_id = get_user_id(message)
        if not is_authorized(user_id):
            await send_message(message, "❌ You are not authorized to access settings!")
            return

        # Create listener for settings
        listener = StreamripListener(message, isLeech=False)

        # Show settings menu
        await show_settings_menu(listener)
    
    # Cancel command
    async def cancel_command(_, message):
        from utils.message_utils import send_message
        from utils.bot_utils import get_user_id
        
        user_id = get_user_id(message)
        cancelled_count = 0
        
        for task_id, task in list(task_dict.items()):
            if hasattr(task, 'listener') and task.listener.user_id == user_id:
                if hasattr(task, 'cancel_download'):
                    task.cancel_download()
                cancelled_count += 1
                task_dict.pop(task_id, None)
        
        if cancelled_count > 0:
            await send_message(message, f"✅ Cancelled {cancelled_count} download(s)")
        else:
            await send_message(message, "❌ No active downloads to cancel")
    
    # Callback query handler for quality selector and settings
    async def handle_callback_query(_, callback_query):
        user_id = callback_query.from_user.id

        # Check for active quality selector
        quality_selector = get_active_quality_selector(user_id)
        if quality_selector and callback_query.data.startswith("srq"):
            await quality_selector._handle_callback(_, callback_query, quality_selector)
            return

        # Check for settings callbacks
        if await handle_settings_callback(_, callback_query):
            return

        # Answer unknown callbacks
        try:
            await callback_query.answer("Unknown callback")
        except Exception:
            pass
    
    # Register handlers
    bot.add_handler(MessageHandler(start_command, filters.command(BotCommands.StartCommand)))
    bot.add_handler(MessageHandler(help_command, filters.command(BotCommands.HelpCommand)))
    bot.add_handler(MessageHandler(status_command, filters.command(BotCommands.StatusCommand)))
    bot.add_handler(MessageHandler(settings_command, filters.command(BotCommands.SettingsCommand)))
    bot.add_handler(MessageHandler(cancel_command, filters.command(BotCommands.CancelCommand)))
    
    # Streamrip commands
    streamrip_mirror_commands = [
        BotCommands.StreamripMirrorCommand,
        BotCommands.SripCommand,
        BotCommands.SrCommand
    ]
    
    streamrip_leech_commands = [
        BotCommands.StreamripLeechCommand,
        BotCommands.SripLeechCommand,
        BotCommands.SrLeechCommand
    ]
    
    streamrip_search_commands = [
        BotCommands.StreamripSearchCommand,
        BotCommands.SripSearchCommand,
        BotCommands.SrSearchCommand
    ]
    
    for cmd in streamrip_mirror_commands:
        bot.add_handler(MessageHandler(StreamripCommands.streamrip_mirror, filters.command(cmd)))
    
    for cmd in streamrip_leech_commands:
        bot.add_handler(MessageHandler(StreamripCommands.streamrip_leech, filters.command(cmd)))
    
    for cmd in streamrip_search_commands:
        bot.add_handler(MessageHandler(StreamripCommands.streamrip_search, filters.command(cmd)))
    
    # Callback query handler
    bot.add_handler(CallbackQueryHandler(handle_callback_query))
    
    LOGGER.info("Command handlers registered successfully")


async def set_bot_commands():
    """Set bot commands in Telegram UI"""
    try:
        from pyrogram.types import BotCommand
        from commands.bot_commands import BotCommands
        
        commands = [
            BotCommand(BotCommands.SrCommand, "Download music (mirror)"),
            BotCommand(BotCommands.SrLeechCommand, "Download music (leech)"),
            BotCommand(BotCommands.SrSearchCommand, "Search music"),
            BotCommand(BotCommands.StatusCommand, "Show download status"),
            BotCommand(BotCommands.SettingsCommand, "Configure bot settings"),
            BotCommand(BotCommands.CancelCommand, "Cancel downloads"),
            BotCommand(BotCommands.HelpCommand, "Show help"),
        ]
        
        await bot.set_bot_commands(commands)
        LOGGER.info("Bot commands set successfully")
        
    except Exception as e:
        LOGGER.error(f"Failed to set bot commands: {e}")


if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"Fatal error: {e}")
        sys.exit(1)
