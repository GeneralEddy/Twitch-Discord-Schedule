# Twitch Schedule Discord Bot

A Discord bot that automatically posts and updates your Twitch stream schedule as a pinned embed in your Discord server. Updates every 5 minutes, shows live/offline status, and displays times in each viewer's local timezone.

![Preview](https://raw.githubusercontent.com/GeneralEddy/Twitch-Discord-Schedule/main/Stream%20Schedule%20Bot.png)

## Features

- 📅 Pulls your schedule directly from Twitch
- 🔴 Live/offline detection with colour change
- 🕒 Discord timestamps — every viewer sees times in their own timezone
- 🖼️ Automatically pulls your Twitch profile picture
- 📌 One pinned message, edited in place — no spam
- 🔁 Updates every 5 minutes automatically
- 📢 Updates channel topic with next stream info

---

## Requirements

- Python 3.11 or higher
- A Discord account
- A Twitch account

---

## Setup

### 1. Create a Discord Bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** and give it a name
3. Go to the **Bot** tab → click **Reset Token** → copy the token
4. Scroll down and enable **Message Content Intent**
5. Go to **OAuth2 → URL Generator**:
   - Tick **bot** under Scopes
   - Tick **Send Messages**, **Manage Messages**, **Embed Links**, **Read Message History** under Bot Permissions
6. Copy the generated URL and open it in your browser to invite the bot to your server

### 2. Create a Twitch App

1. Go to [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps)
2. Click **Register Your Application**
3. Set OAuth Redirect URL to `https://localhost` and click **Add**
4. Set Category to **Other**
5. Click **Create**
6. Click **Manage** on your new app
7. Copy your **Client ID**
8. Click **New Secret** and copy your **Client Secret**

### 3. Get Your Discord Channel ID

1. In Discord, go to **Settings → Advanced** and enable **Developer Mode**
2. Right-click the channel you want the schedule in
3. Click **Copy Channel ID**

### 4. Configure the Bot

1. Copy `.env.example` to `.env`
2. Fill in your values:

```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_channel_id
TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
TWITCH_CHANNEL=your_twitch_username
```

### 5. Install Dependencies

```
pip install -r requirements.txt
```

### 6. Run the Bot

```
python bot.py
```

The bot will post and pin the schedule embed on first run, then update it every 5 minutes automatically.

---

## Auto-Start on Windows (Optional)

This makes the bot start automatically every time you log into Windows — silently, with no terminal window. Once set up, you never need to manually run the bot again.

1. Open Command Prompt as Administrator (right-click Start → Terminal (Admin))
2. Run the command below, replacing `C:\path\to\schedule-bot` with the actual path to your bot folder:

```
schtasks /create /tn "DiscordScheduleBot" /tr "wscript.exe \"C:\path\to\schedule-bot\run_bot.vbs\"" /sc onlogon /delay 0001:00 /ru "%USERNAME%" /f
```

3. To start it immediately without rebooting, run:

```
schtasks /run /tn "DiscordScheduleBot"
```

The bot will now run silently in the background every time you log in, updating your Discord embed every 5 minutes automatically.

---

## File Structure

```
schedule-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env.example        # Template for your credentials
├── run_bot.bat         # Windows launch script
├── run_bot.vbs         # Silent launcher (no terminal window)
└── .gitignore          # Keeps your .env out of Git
```

---

## Contributing

Pull requests welcome. If you find a bug or want a feature, open an issue.

---

## License

MIT — free to use, modify, and share.
