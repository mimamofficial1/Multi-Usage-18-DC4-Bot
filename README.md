# 🤖 Muzaffar Multi Usage Bot

A feature-rich Telegram bot with video/audio processing, URL downloading, file management and much more.

---

## ✨ Features

### 🎬 Video Tools (19)
| # | Feature |
|---|---------|
| 1 | Audio & Subtitles Remover |
| 2 | Audio & Subtitles Extractor |
| 3 | Caption & Buttons Editor |
| 4 | Video Trimmer |
| 5 | Video Merger |
| 6 | Mute Audio in Video |
| 7 | Video + Audio Merger |
| 8 | Video + Subtitle Merger |
| 9 | Video to GIF Converter |
| 10 | Video Splitter |
| 11 | Screenshot Generator |
| 12 | Manual Screenshot |
| 13 | Video Sample Generator |
| 14 | Audio Converter (mp3, wav, flac, aac, ogg, opus, m4a, wma, ac3) |
| 15 | Video Optimizer |
| 16 | Video Converter (mp4, mkv, avi, m4v, mov) |
| 17 | Video Renamer |
| 18 | Media Information |
| 19 | Make Archive (zip) |

### 🎵 Audio Tools (17)
| # | Feature |
|---|---------|
| 1 | Caption & Buttons Editor |
| 2 | Slowed & Reverb Maker |
| 3 | Audio Converter (mp3, wav, flac, aac, ogg, etc.) |
| 4 | Make Archive |
| 5 | Audio Merger |
| 6 | 8D Audio Converter |
| 7 | Music Equalizer |
| 8 | Bass Booster |
| 9 | Treble Booster |
| 10 | Audio Trimmer |
| 11 | Auto Audio Trimmer |
| 12 | Rename Audio |
| 13 | Audio Tag Editor |
| 14 | Speed Changer (50–200%) |
| 15 | Volume Changer (10–200%) |
| 16 | Media Information |
| 17 | Compress Audio |

### 📄 Document Tools (7)
| # | Feature |
|---|---------|
| 1 | File Renamer |
| 2 | Create Archive (zip) |
| 3 | Archive Extractor |
| 4 | Caption & Buttons Editor |
| 5 | Forwarded Tag Remover |
| 6 | Subtitle Converter |
| 7 | JSON Formatter |

### 🔗 URL Tools (6)
| # | Feature |
|---|---------|
| 1 | Extract Archive via Direct Link |
| 2 | URL Uploader (Link → File) |
| 3 | Link Shortener |
| 4 | Link Unshortener |
| 5 | Google Drive Downloader |
| 6 | YT / Social Media Downloader |

---

## 🚀 Deployment on Railway

### Step 1 – Create a Bot
1. Open Telegram → search **@BotFather**
2. Send `/newbot` and follow instructions
3. Copy your **BOT_TOKEN**

### Step 2 – Create MongoDB Atlas database (free)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster → get the connection string
3. Replace `user:pass` with your credentials in the URI

### Step 3 – Deploy to Railway
1. Fork / upload this project to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select your repository
4. Go to **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | your bot token |
| `MONGO_URI` | your MongoDB URI |
| `ADMIN_IDS` | your Telegram user ID |
| `LOG_CHANNEL` | (optional) channel ID |

5. Click **Deploy** ✅

### Step 4 – Verify System Dependencies
Railway automatically installs packages from `requirements.txt`.
FFmpeg and aria2c are required — add a `nixpacks.toml` file:

```toml
[phases.setup]
nixPkgs = ["ffmpeg", "aria2", "p7zip"]
```

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Show basic commands |
| `/info` | Show your account details |
| `/upgrade` | Check subscription status |
| `/plan` | View available plans |
| `/settings` | Configure bot settings |
| `/usettings` | User settings (caption, prefix, etc.) |
| `/bulk_url` | Bulk URL downloader |
| `/show_thumb` | Show saved thumbnail |
| `/del_thumb` | Delete saved thumbnail |
| `/json_formatter` | JSON formatting tool |
| `/cancel` | Cancel current task |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/admin` | List admin commands |
| `/status` | Bot & server status |
| `/broadcast` | Broadcast to all users |
| `/paid <uid> <plan> <days>` | Activate plan for user |
| `/ban_user <uid>` | Ban a user |
| `/unban_user <uid>` | Unban a user |
| `/banned_users` | List banned users |
| `/log` | Download bot logs |
| `/restart` | Restart the bot |

---

## 🛠 Local Development

```bash
git clone https://github.com/yourname/muzaffar-bot.git
cd muzaffar-bot

# Install dependencies
pip install -r requirements.txt

# Install system tools (Ubuntu/Debian)
sudo apt install ffmpeg aria2 p7zip-full

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run
python main.py
```

---

## 📞 Support
Contact: @Dark_of_Danger
