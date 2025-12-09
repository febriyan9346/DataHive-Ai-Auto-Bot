# DataHive AI Auto Bot

Automated farming bot for DataHive AI that helps you earn points automatically through worker uptime and periodic pings.

## Features

- 🤖 **Automated Farming** - Continuous uptime tracking and point accumulation
- 🔄 **Multi-Account Support** - Manage multiple accounts simultaneously
- 🌐 **Proxy Support** - Run with free Proxyscrape proxies, private proxies, or without proxy
- 🔁 **Smart Proxy Rotation** - Automatically rotate proxies on connection failures
- 📊 **Real-time Statistics** - Monitor 24h points and total points for each account
- 🎨 **Beautiful Console UI** - Color-coded terminal output with clear status indicators
- ⏱️ **WIB Timezone** - Timestamps in Western Indonesian Time (Asia/Jakarta)

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/febriyan9346/DataHive-Ai-Auto-Bot.git
cd DataHive-Ai-Auto-Bot
```

2. **Install required packages**
```bash
pip install -r requirements.txt
```

3. **Configure your accounts**
   - Open `accounts.txt`
   - Add your DataHive bearer tokens (one per line)
   - To get your token:
     1. Login to DataHive AI web app
     2. Open browser DevTools (F12)
     3. Go to Network tab
     4. Look for API requests to `api.datahive.ai`
     5. Copy the Bearer token from the Authorization header

4. **Configure proxies (Optional)**
   - Open `proxy.txt`
   - Add your proxies (one per line)
   - Supported formats:
     - `http://ip:port`
     - `https://ip:port`
     - `socks4://ip:port`
     - `socks5://ip:port`
     - `ip:port` (will default to http)

## Usage

Run the bot:
```bash
python bot.py
```

### Proxy Options

When you start the bot, you'll be asked to choose:

1. **Run With Free Proxyscrape Proxy** - Automatically downloads and uses free proxies
2. **Run With Private Proxy** - Uses proxies from your `proxy.txt` file
3. **Run Without Proxy** - Direct connection without proxy

If you choose proxy options, you'll also be asked:
- **Rotate Invalid Proxy?** - Auto-rotate to next proxy on connection failures

### How It Works

1. The bot loads all accounts from `accounts.txt`
2. Assigns a proxy to each account (if enabled)
3. Fetches worker information and displays current points
4. Sends periodic ping requests every 60 seconds
5. Checks worker IP and updates point statistics
6. Displays total and average points across all accounts

## File Structure

```
DataHive-Ai-Auto-Bot/
│
├── bot.py              # Main bot script
├── accounts.txt        # Your DataHive tokens (one per line)
├── proxy.txt           # Your proxy list (optional)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Configuration Files

### accounts.txt
```
Bearer_token_account_1
Bearer_token_account_2
Bearer_token_account_3
```

### proxy.txt
```
http://proxy1.com:8080
socks5://proxy2.com:1080
192.168.1.1:3128
```

## Output Example

```
[ 12/09/24 15:30:45 WIB ] | Account's Total: 3
[ 12/09/24 15:30:45 WIB ] | Proxies Total: 50
===========================================================================
[ 12/09/24 15:30:46 WIB ] | [ Account: use***@email.com - Proxy: http://proxy.com:8080 - Status: 24h: 125.50 PTS - Total: 1250.75 PTS ]
[ 12/09/24 15:30:47 WIB ] | [ Account: use***@email.com - Proxy: http://proxy.com:8080 - Status: PING Success ]
[ 12/09/24 15:30:48 WIB ] | [ Account: use***@email.com - Proxy: http://proxy.com:8080 - Status: IP Check: 123.456.789.0 ]
===========================================================================
```

## Statistics

The bot tracks:
- **24h Points** - Points earned in the last 24 hours
- **Total Points** - Lifetime points for each account
- **Average Points** - Average points across all accounts
- **Total Sessions** - Number of ping cycles completed
- **Total Pings** - Total API calls made

## Troubleshooting

### Common Issues

1. **"Failed Get Info: Status 401"**
   - Your bearer token has expired
   - Login again and get a new token

2. **"Connection Failed"**
   - Check your internet connection
   - Try using a different proxy
   - Enable proxy rotation

3. **"No Accounts Loaded"**
   - Ensure `accounts.txt` exists and contains valid tokens
   - Check file is in the same directory as `bot.py`

4. **Proxy Issues**
   - Verify proxy format is correct
   - Test proxies are working
   - Enable auto-rotation for invalid proxies

## Safety & Best Practices

- ✅ Use different proxies for each account
- ✅ Don't run too many accounts simultaneously
- ✅ Keep your tokens secure and private
- ✅ Enable proxy rotation to avoid rate limits
- ⚠️ Use at your own risk - automated farming may violate ToS

## Contributing

Feel free to submit issues and enhancement requests!

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The developer is not responsible for any consequences that may arise from using this bot, including but not limited to account bans or violations of DataHive AI's Terms of Service.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you find this bot helpful, consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features

---

**Created by:** [febriyan9346](https://github.com/febriyan9346)

**Last Updated:** December 2024
