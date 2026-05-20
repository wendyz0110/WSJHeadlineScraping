# WSJ Headlines Scraper

Scrapes article headlines from the WSJ archive and saves them to a CSV file.

## Requirements

pip install undetected-chromedriver selenium pandas
Also requires Google Chrome to be installed.

## Usage

1. Update the credentials at the bottom of the script:
```python
   EMAIL = "your_email"
   PASSWORD = "your_password"
```
2. Run the script:
```bash
   python WSJ_ScrapingUndetected.py
```

The script logs into WSJ, scrapes headlines day by day from July 1, 2024 to today, and saves them to `wsj_headlines.csv`.

## Output

A CSV file with two columns: `date` and `headline`, ordered earliest-to-latest within each day.

## Notes

- If a CAPTCHA appears during login, solve it manually in the browser window and press Enter to continue.
- The script retries each day up to 3 times if scraping fails.
