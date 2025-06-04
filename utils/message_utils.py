import asyncio
from logging import getLogger

LOGGER = getLogger(__name__)


async def send_message(message, text, buttons=None, photo=None, **kwargs):
    """Send a message to Telegram"""
    try:
        if photo:
            return await message.reply_photo(
                photo, caption=text, reply_markup=buttons, **kwargs
            )
        else:
            return await message.reply_text(text, reply_markup=buttons, **kwargs)
    except Exception as e:
        LOGGER.error(f"Error sending message: {e}")
        return None


async def edit_message(message, text, buttons=None, **kwargs):
    """Edit a message"""
    try:
        if buttons:
            return await message.edit_text(text, reply_markup=buttons, **kwargs)
        else:
            return await message.edit_text(text, **kwargs)
    except Exception as e:
        LOGGER.error(f"Error editing message: {e}")
        return None


async def delete_message(message):
    """Delete a message"""
    try:
        await message.delete()
        return True
    except Exception as e:
        LOGGER.error(f"Error deleting message: {e}")
        return False


async def auto_delete_message(message, time=300):
    """Auto delete a message after specified time"""
    try:
        await asyncio.sleep(time)
        await delete_message(message)
    except Exception as e:
        LOGGER.error(f"Error auto-deleting message: {e}")


async def send_status_message(message, text, **kwargs):
    """Send a status message"""
    return await send_message(message, text, **kwargs)


async def update_status_message(chat_id):
    """Update status message for a chat"""
    # This would be implemented based on your status system
    pass
