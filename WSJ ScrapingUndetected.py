import time
import csv
from datetime import date, timedelta
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# --- Setup Driver ---
options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# --- Login ---
def handle_captcha():
    time.sleep(2)
    page = driver.page_source.lower()
    if "captcha" in page or "slider" in page or "verification" in page:
        print("CAPTCHA detected! Please solve it in the browser.")
        input("Once solved and password field is visible, press Enter to continue...")

def login(email, password):
    print("Logging in...")
    driver.get("https://www.wsj.com")
    time.sleep(4)

    # Click Sign In
    sign_in = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign In")))
    sign_in.click()
    time.sleep(3)

    # Step 1: Enter email
    email_field = wait.until(EC.presence_of_element_located((By.NAME, "emailOrUsername")))
    email_field.send_keys(email)
    time.sleep(1.5)

    # Click Continue
    continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
    continue_btn.click()
    handle_captcha()  # ← dynamic check after Continue

    # Step 2: Enter password
    password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "fieldset[data-slot='input-group'] input")))
    password_field.send_keys(password)
    time.sleep(1.5)

    # Click Sign In
    submit = wait.until(EC.element_to_be_clickable((By.ID, "signin-pass-submit-btn")))
    submit.click()
    handle_captcha()  # ← dynamic check after Sign In too

    # Handle "Verify your Email" screen if it appears
    try:
        continue_wsj = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue to WSJ')]")
        continue_wsj.click()
        time.sleep(2)
    except:
        pass

    print("Login successful!")

def scrape_day(target_date, retries=3):
    url = f"https://www.wsj.com/news/archive/{target_date.strftime('%Y/%m/%d')}"
    
    for attempt in range(retries):
        driver.get(url)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='HeadlineTextBlock']")))
            headlines = driver.find_elements(By.CSS_SELECTOR, "div[class*='HeadlineTextBlock']")
            results = []
            for h in headlines:
                text = h.text.strip()
                if text:
                    results.append({
                        "date": target_date.strftime("%Y-%m-%d"),
                        "headline": text
                    })
            if results:  # only return if we actually got something
                return results
            else:
                print(f"  Attempt {attempt+1}: 0 headlines, retrying...")
                time.sleep(3)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: retrying in 3 seconds...")
            time.sleep(3)
    
    print(f"  All {retries} attempts failed for {target_date}")
    return []

# --- Main ---
EMAIL = "your email"   
PASSWORD = "your password"      

login(EMAIL, PASSWORD)

start_date = date(2024, 7, 1)
end_date = date.today()
current_date = start_date
all_results = [] 

while current_date <= end_date:
    print(f"Scraping {current_date}...")
    day_results = scrape_day(current_date)
    all_results.extend(day_results)
    print(f"  → {len(day_results)} headlines found")
    time.sleep(1.5)
    current_date += timedelta(days=1)

driver.quit()

# --- Save to CSV ---
with open("wsj_headlines.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "headline"])
    writer.writeheader()
    writer.writerows(all_results)

# --- Reverse order within each day (early to late) ---
df = pd.read_csv("wsj_headlines.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.groupby(df['date'].dt.date, group_keys=False).apply(lambda x: x.iloc[::-1])
df.to_csv("wsj_headlines.csv", index=False)

print(f"Done! {len(all_results)} total headlines saved to wsj_headlines.csv")



















