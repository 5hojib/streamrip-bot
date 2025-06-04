from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ButtonMaker:
    """Helper class to build inline keyboard buttons"""

    def __init__(self):
        self._buttons = []
        self._footer_buttons = []

    def data_button(self, text, callback_data, position="main"):
        """Add a callback data button"""
        button = InlineKeyboardButton(text, callback_data=callback_data)
        if position == "footer":
            self._footer_buttons.append(button)
        else:
            self._buttons.append(button)

    def url_button(self, text, url, position="main"):
        """Add a URL button"""
        button = InlineKeyboardButton(text, url=url)
        if position == "footer":
            self._footer_buttons.append(button)
        else:
            self._buttons.append(button)

    def build_menu(self, n_cols=1, footer_cols=2):
        """Build the inline keyboard markup"""
        menu = []

        # Add main buttons
        for i in range(0, len(self._buttons), n_cols):
            menu.append(self._buttons[i : i + n_cols])

        # Add footer buttons
        if self._footer_buttons:
            for i in range(0, len(self._footer_buttons), footer_cols):
                menu.append(self._footer_buttons[i : i + footer_cols])

        return InlineKeyboardMarkup(menu) if menu else None

    def clear(self):
        """Clear all buttons"""
        self._buttons.clear()
        self._footer_buttons.clear()
