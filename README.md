# Telegram Message Forwarder Bot

A Telegram bot that monitors specific users in a group and forwards their messages to another group. Runs in **user mode** (using your own Telegram account), so no need to add any bot to the source group.

## Features

- Monitor specific users by username
- Forward all message types (text, photos, videos, documents, etc.)
- Custom message format: `@username: message content`
- Pause/Resume forwarding
- Configure via Telegram commands (no need to edit files)
- Runs 24/7 on a server

## Prerequisites

- Python 3.8+
- Telegram account
- API credentials from [my.telegram.org](https://my.telegram.org)

## Getting API Credentials

1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click **"API development tools"**
4. Create a new application:
   - App title: `Forwarder` (any name)
   - Short name: `forwarder` (any name)
   - Platform: `Desktop`
5. Copy your **API_ID** and **API_HASH**

## Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/junjieooi/tg-forward-bot.git
cd tg-forward-bot

# Install dependencies
pip install -r requirements.txt

# Create config file
cp .env.example .env

# Edit config
nano .env
```

Add your credentials to `.env`:
```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890
```

### First Run

```bash
python3 main.py
```

On first run, you'll need to enter a verification code sent to your Telegram.

## Configuration Commands

Send these commands to yourself in **Saved Messages**:

| Command | Description |
|---------|-------------|
| `/setadmin` | Set yourself as admin (first time only) |
| `/setsourceid -100xxx` | Set source group by ID |
| `/settargetid -100xxx` | Set target group by ID |
| `/setsource` | Set source group (send in the group) |
| `/settarget` | Set target group (send in the group) |
| `/adduser @username` | Add user to monitor |
| `/removeuser @username` | Remove user from monitoring |
| `/listusers` | List monitored users |
| `/status` | View current configuration |
| `/pause` | Pause forwarding |
| `/resume` | Resume forwarding |
| `/help` | Show help |

## Setup Steps

1. **Set admin** - Send `/setadmin` to Saved Messages
2. **Set source group** - Send `/setsourceid -100xxxxxxxxxx` (get ID from [@userinfobot](https://t.me/userinfobot) or web.telegram.org)
3. **Set target group** - Send `/settarget` in the target group
4. **Add users** - Send `/adduser @username` for each user to monitor
5. **Check config** - Send `/status` to verify

## Getting Group ID

### Method 1: Using @userinfobot
1. Add [@userinfobot](https://t.me/userinfobot) to the group
2. It will display the group ID
3. Remove the bot after

### Method 2: Using Web Telegram
1. Open [https://web.telegram.org/a/](https://web.telegram.org/a/)
2. Enter the group
3. Check the URL: `https://web.telegram.org/a/#-1234567890`
4. Add `-100` prefix: `-1001234567890`

---

# Server Deployment (DigitalOcean/Ubuntu)

## 1. Connect to Server

```bash
ssh username@your_server_ip
```

## 2. Install Dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```

## 3. Clone Repository

```bash
cd ~
git clone https://github.com/junjieooi/tg-forward-bot.git
cd tg-forward-bot
```

For private repos:
```bash
git clone https://username:token@github.com/junjieooi/tg-forward-bot.git
```

## 4. Install Python Packages

```bash
pip install -r requirements.txt
```

## 5. Configure

```bash
cp .env.example .env
nano .env
```

Fill in your credentials:
```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890
```

Save: `Ctrl+X` → `Y` → `Enter`

## 6. First Run (Authentication)

```bash
python3 main.py
```

- Enter the verification code sent to your Telegram
- Once logged in, press `Ctrl+C` to stop

## 7. Create Systemd Service

```bash
sudo nano /etc/systemd/system/tgbot.service
```

Paste:
```ini
[Unit]
Description=Telegram Forward Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/tg-forward-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `your_username` with your actual username (e.g., `trader`).

Save: `Ctrl+X` → `Y` → `Enter`

## 8. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot
```

## 9. Verify

```bash
sudo systemctl status tgbot
```

Should show `Active: active (running)`.

## Service Management

```bash
# Start
sudo systemctl start tgbot

# Stop
sudo systemctl stop tgbot

# Restart
sudo systemctl restart tgbot

# View logs
sudo journalctl -u tgbot -f

# Check status
sudo systemctl status tgbot
```

## Updating

```bash
cd ~/tg-forward-bot
git pull
sudo systemctl restart tgbot
```

---

## Security Notes

- Never share your `.env` file
- Never share your `.session` file
- Keep your server secure (use SSH keys, strong passwords)
- Consider using a secondary Telegram account

## Troubleshooting

### Database locked error
```bash
pkill -f "python3 main.py"
rm -f forwarder_session.session-journal
python3 main.py
```

### Bot not responding to commands
- Make sure you're sending commands to **Saved Messages**
- Check if you've set yourself as admin with `/setadmin`
- Check logs: `sudo journalctl -u tgbot -f`

### Messages not forwarding
- Check `/status` to verify configuration
- Make sure bot is not paused (`/resume`)
- Verify the monitored username is correct (case-insensitive, without @)

## License

MIT License
