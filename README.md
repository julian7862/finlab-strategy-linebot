# finlab-strategy-linebot

A Python bot that scrapes Finlab strategy stock data and sends notifications to LINE Bot.

## Features

- 🔍 Automated web scraping of Finlab strategy holdings
- 📱 LINE Bot integration for instant notifications
- 🧪 Comprehensive unit tests (22 tests, 69% coverage)
- 🐳 Environment variable support for easy deployment
- 🔄 CI/CD ready with GitHub Actions

## Prerequisites

- **Python 3.13.3** (recommended)
- Chrome/Chromium browser
- LINE Bot Channel (for notifications)

## Setup Instructions

### Step 1: Create Virtual Environment

```bash
# Create virtual environment with Python 3.13
python3.13 -m venv venv
```

### Step 2: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

**Option A: Using .env file (recommended for local development)**

```bash
# Copy the example file
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

Update the following variables in `.env`:
```env
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
LINE_USER_ID=your_line_user_id_here
TARGET_URL=https://your_target_website_here
CHROME_DRIVER_PATH=/usr/local/bin/chromedriver  # Optional
```

**Option B: Using OS environment variables (for deployment)**

```bash
export TARGET_URL=https://your_target_website_here
export LINE_CHANNEL_ACCESS_TOKEN=your_token_here
export LINE_USER_ID=your_user_id_here
```

> **Note:** OS environment variables take priority over `.env` file values.

### Step 5: Run the Application

```bash
python main.py
```

## Project Structure

```
finlab-strategy-linebot/
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your config (not in git)
│
├── src/
│   ├── scraper.py            # Web scraping logic
│   ├── line_notification.py  # LINE Bot integration
│   └── utils/
│       ├── config.py         # Configuration management
│       └── formatter.py      # Output formatting
│
├── tests/
│   ├── test_scraper.py       # Scraper unit tests
│   ├── test_line_notification.py  # LINE Bot tests
│   └── test_config.py        # Config tests
│
└── .github/
    └── workflows/
        └── main.yml          # GitHub Actions CI/CD
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_scraper.py -v
```

## How It Works

1. **Scraping**: Uses Selenium to navigate to the target website, switch into iframe, click the "選股" tab, and extract stock data
2. **Formatting**: Formats the scraped data into a readable format
3. **Notification**: Sends formatted data to LINE Bot (if credentials are configured)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TARGET_URL` | ✅ Yes | URL of the Finlab strategy page |
| `LINE_CHANNEL_ACCESS_TOKEN` | ⚠️ Optional | LINE Bot channel access token |
| `LINE_USER_ID` | ⚠️ Optional | LINE user ID to send messages to |
| `LINE_WEBHOOK_URL` | ❌ No | LINE webhook URL (future use) |
| `CHROME_DRIVER_PATH` | ❌ No | Custom ChromeDriver path |

## Development

### Install development dependencies

Already included in `requirements.txt`:
- pytest
- pytest-mock
- pytest-cov

### Code structure

- **Clean Architecture**: Separated concerns (scraping, notification, formatting)
- **Modular Design**: Each component is independently testable
- **Type Safety**: Clear interfaces and error handling

## Deployment

The application supports deployment to various platforms:

**Docker:**
```dockerfile
ENV TARGET_URL=https://production.com
ENV LINE_CHANNEL_ACCESS_TOKEN=prod_token
ENV LINE_USER_ID=prod_user_id
```

**Heroku:**
```bash
heroku config:set TARGET_URL=https://production.com
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=prod_token
heroku config:set LINE_USER_ID=prod_user_id
```

**GitHub Actions:**
CI/CD workflow is already configured in `.github/workflows/main.yml`

## Troubleshooting

**Issue: ChromeDriver not found**
```bash
# Install via webdriver-manager (automatic)
# Or manually specify path in .env:
CHROME_DRIVER_PATH=/path/to/chromedriver
```

**Issue: Tests failing**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: LINE notification not working**
- Verify `LINE_CHANNEL_ACCESS_TOKEN` is correct
- Verify `LINE_USER_ID` is correct
- Check LINE Bot console for errors

## License

MIT

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request