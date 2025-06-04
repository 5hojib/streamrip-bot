# Streamrip Bot

A standalone Telegram bot for downloading high-quality music from various streaming platforms using [streamrip](https://github.com/nathom/streamrip).

## Features

🎵 **Multi-Platform Support**
- 🟦 **Qobuz** - Up to 24-bit/192kHz FLAC
- ⚫ **Tidal** - MQA and Hi-Res FLAC  
- 🟣 **Deezer** - CD Quality FLAC
- 🟠 **SoundCloud** - MP3 320kbps

🎛️ **Quality Options**
- 128 kbps (Low quality)
- 320 kbps (High quality) 
- CD Quality (16-bit/44.1kHz FLAC)
- Hi-Res (24-bit/≤96kHz FLAC/MQA)
- Hi-Res+ (24-bit/≤192kHz FLAC)

🎵 **Format Support**
- FLAC (Lossless)
- MP3 (Lossy)
- M4A/AAC (Lossy)
- OGG Vorbis (Lossy)
- Opus (Lossy)

⚡ **Advanced Features**
- Interactive quality selector
- Batch downloads from files
- Search across platforms
- Last.fm playlist conversion
- Mirror to cloud storage
- Leech to Telegram

## Installation

### Prerequisites

- Python 3.9 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamrip
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp config_sample.py config.py
   ```
   
   Edit `config.py` with your credentials:
   ```python
   BOT_TOKEN = "your_bot_token"
   OWNER_ID = your_telegram_user_id
   TELEGRAM_API = your_api_id
   TELEGRAM_HASH = "your_api_hash"
   ```

4. **Configure streaming platforms**
   
   Add your streaming service credentials to `config.py`:
   
   **Qobuz:**
   ```python
   STREAMRIP_QOBUZ_EMAIL = "your_email"
   STREAMRIP_QOBUZ_PASSWORD = "your_password"
   ```
   
   **Tidal:**
   ```python
   STREAMRIP_TIDAL_ACCESS_TOKEN = "your_access_token"
   STREAMRIP_TIDAL_REFRESH_TOKEN = "your_refresh_token"
   ```
   
   **Deezer:**
   ```python
   STREAMRIP_DEEZER_ARL = "your_arl_cookie"
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

## Usage

### Basic Commands

- `/sr <url>` - Download music (mirror mode)
- `/srleech <url>` - Download music (leech to Telegram)
- `/srsearch <query>` - Search for music
- `/status` - Show download status
- `/settings` - Configure bot settings
- `/cancel` - Cancel your downloads
- `/help` - Show help message

### Advanced Usage

**Quality and format selection:**
```
/sr -q 3 -c flac https://qobuz.com/album/...
```

**Search and download:**
```
/srsearch artist name - album title
```

**Batch downloads:**
```
/sr file_with_urls.txt
```

### Supported URL Formats

- **Qobuz:** `https://qobuz.com/album/...`
- **Tidal:** `https://tidal.com/browse/album/...`
- **Deezer:** `https://deezer.com/album/...`
- **SoundCloud:** `https://soundcloud.com/artist/track`
- **Last.fm:** `https://last.fm/user/username/playlists/...`

### Quality Levels

| Level | Quality | Description | Platforms |
|-------|---------|-------------|-----------|
| 0 | 128 kbps | Low quality MP3/AAC | All |
| 1 | 320 kbps | High quality MP3/AAC | All |
| 2 | CD Quality | 16-bit/44.1kHz FLAC | All |
| 3 | Hi-Res | 24-bit/≤96kHz FLAC/MQA | Tidal, Qobuz |
| 4 | Hi-Res+ | 24-bit/≤192kHz FLAC | Qobuz |

## Configuration

### Required Settings

```python
# Bot credentials
BOT_TOKEN = "your_bot_token"
OWNER_ID = your_user_id
TELEGRAM_API = your_api_id
TELEGRAM_HASH = "your_api_hash"
```

### Optional Settings

```python
# Download settings
DOWNLOAD_DIR = "/path/to/downloads/"
LEECH_SPLIT_SIZE = 2097152000  # 2GB
AS_DOCUMENT = False
MEDIA_GROUP = True

# Streamrip settings
STREAMRIP_DEFAULT_QUALITY = 3
STREAMRIP_DEFAULT_CODEC = "flac"
STREAMRIP_CONCURRENT_DOWNLOADS = 4
```

## Platform Setup

### Qobuz
1. Sign up for a Qobuz account
2. Add email and password to config

### Tidal
1. Use the token generator script:
   ```bash
   python dev/tidal_tokens.py
   ```
2. Add tokens to config

### Deezer
1. Get ARL cookie from browser
2. Add to config

### SoundCloud
- Works without authentication
- Optional client ID for better reliability

## Troubleshooting

### Common Issues

**"Streamrip is not available"**
- Install streamrip: `pip install git+https://github.com/shabbirmahmud/streamrip.git@dev`

**"No streamrip platforms are configured"**
- Add credentials for at least one platform in config.py

**"Invalid streamrip URL"**
- Check if the URL is from a supported platform
- Ensure the URL is complete and valid

**Quality not available**
- Some qualities require premium subscriptions
- Bot will fallback to available quality

### Logs

Check `streamrip_bot.log` for detailed error messages.

## Development

### Project Structure

```
streamrip/
├── bot.py                 # Main bot file
├── config_manager.py      # Configuration manager
├── config_sample.py       # Sample configuration
├── settings.py           # Settings UI interface
├── requirements.txt      # Dependencies
├── commands/            # Command handlers
├── download/           # Download management
├── listeners/          # Event listeners
├── status/            # Status tracking
├── streamrip_utils/   # Streamrip utilities
└── utils/            # General utilities
```

### Adding Features

1. Create new modules in appropriate directories
2. Register handlers in `bot.py`
3. Update command definitions in `commands/bot_commands.py`

## License

This project is based on the aimleechbot repository and maintains compatibility with streamrip.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Ensure all dependencies are installed
4. Verify platform credentials are correct

## Credits

- [streamrip](https://github.com/nathom/streamrip) - Core music downloading library
- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram Bot API framework
- [aimleechbot](https://github.com/AeonOrg/Aeon-MLTB) - Original implementation reference
