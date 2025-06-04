"""Bot command definitions for Streamrip Bot"""

from config_manager import Config


class BotCommands:
    """Bot command definitions"""
    
    # Get command suffix
    suffix = Config.CMD_SUFFIX
    
    # Streamrip commands
    StreamripMirrorCommand = f"streamrip{suffix}"
    StreamripLeechCommand = f"streamripleech{suffix}"
    StreamripSearchCommand = f"streamripsearch{suffix}"
    
    # Alternative command names
    SripCommand = f"srip{suffix}"
    SripLeechCommand = f"sripleech{suffix}"
    SripSearchCommand = f"sripsearch{suffix}"
    
    # Short commands
    SrCommand = f"sr{suffix}"
    SrLeechCommand = f"srleech{suffix}"
    SrSearchCommand = f"srsearch{suffix}"
    
    # General commands
    StartCommand = f"start{suffix}"
    HelpCommand = f"help{suffix}"
    StatusCommand = f"status{suffix}"
    SettingsCommand = f"settings{suffix}"
    CancelCommand = f"cancel{suffix}"
    CancelAllCommand = f"cancelall{suffix}"
    
    # Admin commands
    RestartCommand = f"restart{suffix}"
    LogCommand = f"log{suffix}"
    ShellCommand = f"shell{suffix}"
    
    @classmethod
    def get_all_commands(cls):
        """Get all available commands"""
        commands = {}
        
        for attr_name in dir(cls):
            if attr_name.endswith('Command') and not attr_name.startswith('_'):
                command_value = getattr(cls, attr_name)
                if isinstance(command_value, str):
                    commands[attr_name] = command_value
        
        return commands
    
    @classmethod
    def get_streamrip_commands(cls):
        """Get streamrip-specific commands"""
        return {
            "StreamripMirrorCommand": cls.StreamripMirrorCommand,
            "StreamripLeechCommand": cls.StreamripLeechCommand,
            "StreamripSearchCommand": cls.StreamripSearchCommand,
            "SripCommand": cls.SripCommand,
            "SripLeechCommand": cls.SripLeechCommand,
            "SripSearchCommand": cls.SripSearchCommand,
            "SrCommand": cls.SrCommand,
            "SrLeechCommand": cls.SrLeechCommand,
            "SrSearchCommand": cls.SrSearchCommand,
        }
    
    @classmethod
    def get_command_descriptions(cls):
        """Get command descriptions for help"""
        return {
            cls.StreamripMirrorCommand: "Mirror music from streaming platforms",
            cls.StreamripLeechCommand: "Leech music from streaming platforms",
            cls.StreamripSearchCommand: "Search music across platforms",
            cls.SripCommand: "Mirror music (short command)",
            cls.SripLeechCommand: "Leech music (short command)",
            cls.SripSearchCommand: "Search music (short command)",
            cls.SrCommand: "Mirror music (shortest command)",
            cls.SrLeechCommand: "Leech music (shortest command)",
            cls.SrSearchCommand: "Search music (shortest command)",
            cls.StartCommand: "Start the bot",
            cls.HelpCommand: "Show help message",
            cls.StatusCommand: "Show download status",
            cls.SettingsCommand: "Configure bot settings",
            cls.CancelCommand: "Cancel current download",
            cls.CancelAllCommand: "Cancel all downloads",
            cls.RestartCommand: "[ADMIN] Restart the bot",
            cls.LogCommand: "[ADMIN] View bot logs",
            cls.ShellCommand: "[ADMIN] Execute shell commands",
        }


# Command help text
HELP_TEXT = f"""
<b>🎵 Streamrip Bot - Music Downloader</b>

<b>📥 Download Commands:</b>
• <code>/{BotCommands.StreamripMirrorCommand}</code> - Mirror music to cloud storage
• <code>/{BotCommands.StreamripLeechCommand}</code> - Leech music to Telegram
• <code>/{BotCommands.StreamripSearchCommand}</code> - Search music across platforms

<b>🔍 Short Commands:</b>
• <code>/{BotCommands.SrCommand}</code> - Mirror music (short)
• <code>/{BotCommands.SrLeechCommand}</code> - Leech music (short)
• <code>/{BotCommands.SrSearchCommand}</code> - Search music (short)

<b>📋 Usage Examples:</b>
• <code>/{BotCommands.SrCommand} https://qobuz.com/album/...</code>
• <code>/{BotCommands.SrLeechCommand} -q 3 -c flac https://tidal.com/...</code>
• <code>/{BotCommands.SrSearchCommand} artist name - album title</code>

<b>🎛️ Quality Options:</b>
• <code>-q 0</code> - 128 kbps (Low)
• <code>-q 1</code> - 320 kbps (High)
• <code>-q 2</code> - CD Quality (FLAC)
• <code>-q 3</code> - Hi-Res (24-bit)
• <code>-q 4</code> - Hi-Res+ (192kHz)

<b>🎵 Format Options:</b>
• <code>-c flac</code> - FLAC (Lossless)
• <code>-c mp3</code> - MP3 (Lossy)
• <code>-c m4a</code> - M4A/AAC (Lossy)

<b>🎧 Supported Platforms:</b>
🟦 <b>Qobuz</b> - Up to 24-bit/192kHz FLAC
⚫ <b>Tidal</b> - MQA and Hi-Res FLAC
🟣 <b>Deezer</b> - CD Quality FLAC
🟠 <b>SoundCloud</b> - MP3 320kbps

<b>⚙️ General Commands:</b>
• <code>/{BotCommands.StatusCommand}</code> - Show download status
• <code>/{BotCommands.SettingsCommand}</code> - Configure bot settings
• <code>/{BotCommands.CancelCommand}</code> - Cancel current download
• <code>/{BotCommands.HelpCommand}</code> - Show this help message

<b>💡 Tips:</b>
• Use quality selector if no quality specified
• Supports batch downloads from files
• Last.fm playlists are converted automatically
• Premium subscriptions required for high quality

<b>🔗 Example URLs:</b>
• Qobuz: <code>https://qobuz.com/album/...</code>
• Tidal: <code>https://tidal.com/browse/album/...</code>
• Deezer: <code>https://deezer.com/album/...</code>
• SoundCloud: <code>https://soundcloud.com/artist/track</code>
"""

# Start message
START_TEXT = f"""
<b>🎵 Welcome to Streamrip Bot!</b>

This bot can download high-quality music from various streaming platforms.

<b>🚀 Quick Start:</b>
1. Send a music URL from supported platforms
2. Choose quality and format (or use defaults)
3. Get your music in high quality!

<b>📋 Commands:</b>
• <code>/{BotCommands.SrCommand}</code> - Download music
• <code>/{BotCommands.SrSearchCommand}</code> - Search for music
• <code>/{BotCommands.HelpCommand}</code> - Show detailed help

<b>🎧 Supported Platforms:</b>
🟦 Qobuz • ⚫ Tidal • 🟣 Deezer • 🟠 SoundCloud

Type <code>/{BotCommands.HelpCommand}</code> for detailed usage instructions.
"""
