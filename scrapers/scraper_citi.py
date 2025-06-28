import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ────────────── Setup ──────────────

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_experimental_option("prefs", {"profile.managed_content_settings.images": 2})
    driver = webdriver.Chrome(options=options)
    driver.delete_all_cookies()
    return driver

def load_checkboxes(driver):
    driver.get("https://www.citi.com/credit-cards/compare/view-all-credit-cards?vac=CONTROL")

    # Wait for at least one checkbox
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="checkbox"]'))
    )

    time.sleep(1)
    last_count = -1
    retries = 3

    while retries > 0:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
        current_count = len(checkboxes)

        if current_count == last_count:
            retries -= 1
        else:
            last_count = current_count
            retries = 3  # reset

    usable_checkboxes = [cb for cb in checkboxes if cb.is_displayed() and cb.is_enabled()]
    return usable_checkboxes


def get_unprocessed_checkboxes(checkboxes, processed_names):
    unprocessed = []
    for cb in checkboxes:
        label = cb.get_attribute("aria-label")
        if not label:
            continue
        name = re.sub(r"^Compare \(\d+\/3\)\s*", "", label).strip()
        if name not in processed_names:
            cb.card_name = name
            unprocessed.append(cb)
    return unprocessed

# ───────────── Selection Logic ─────────────

def select_cards(driver, unprocessed, checkboxes, processed_names):
    group_names = []
    end_after = False

    if len(unprocessed) == 1:
        cb1 = next((cb for cb in checkboxes if cb.get_attribute("aria-label") and
                    re.sub(r"^Compare \(\d+\/3\)\s*", "", cb.get_attribute("aria-label")).strip() in processed_names), None)
        cb2 = unprocessed[0]
        for cb in [cb1, cb2]:
            if cb:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb)
                cb.click()
                if cb == cb2:
                    group_names.append(cb.card_name)
        end_after = True

    elif len(unprocessed) in [2, 3]:
        for cb in unprocessed:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb)
            cb.click()
            group_names.append(cb.card_name)
        end_after = True

    elif len(unprocessed) >= 4:
        for cb in unprocessed[:3]:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb)
            cb.click()
            group_names.append(cb.card_name)

    return group_names, end_after

def click_compare(driver):
    try:
        btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[normalize-space(text())="Compare now"]'))
        )
    except TimeoutException:
        btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[normalize-space(text())="Compare Now"]'))
        )
    btn.click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Compare Credit Cards")
    )
    # time.sleep(2)

# ───────────── Scraping ─────────────

def get_card_elements(driver, row_index, count):
    cards = []
    for i in range(count):
        if count == 1 and i == 0:
            continue  # Skip first (processed) card
        selector = f"td.featurecard_{row_index}_{i}.item.ng-star-inserted"
        card = driver.find_element(By.CSS_SELECTOR, selector)
        cards.append((i, card))
    return cards

def scrape_results(driver, db, round, count):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-id^='annualFeeAmount']"))
    )

    names = driver.find_elements(By.CSS_SELECTOR, 'h2.card_title.cc-title[id^="selected-credit-card-"]')
    for i, tag in enumerate(names):
        if count == 1 and i == 0:
            continue
        html = tag.get_attribute("innerHTML")
        name = BeautifulSoup(html, "html.parser").text.strip()
        idx = i - 1 + round if count == 1 else i + round
        db[idx]["name"] = name

    row_types = {
        "bonus": 0,
        "reward": 1,
        "fee": 2,
        "apr": 3,
    }

    for key, row in row_types.items():
        cards = get_card_elements(driver, row, count)
        for i, card in cards:
            idx = i - 1 + round if count == 1 else i + round

            if key == "bonus":
                offers = card.find_elements(By.CSS_SELECTOR, 'p.about_content')
                for offer in offers:
                    raw_html = offer.get_attribute("innerHTML")
                    if 'bonusAmount' in raw_html:
                        db[idx]['bonus'] = BeautifulSoup(raw_html, "html.parser").text.strip()

            elif key == "reward":
                rewards = card.find_elements(By.CLASS_NAME, "cardBenefits")
                if rewards:
                    reward_items = BeautifulSoup(rewards[0].get_attribute("innerHTML"), "html.parser").select("li")
                    db[idx]["reward"] = " ".join(r.get_text(" ", strip=True) for r in reward_items)

            elif key == "fee":
                try:
                    fees = card.find_elements(By.CSS_SELECTOR, "span[data-id^='annualFeeAmount']")
                    for fee in fees:
                        html = fee.get_attribute("innerHTML")
                        text = BeautifulSoup(html, "html.parser").get_text(strip=True)
                        db[idx]["fee"] = text
                except:
                    db[idx]["fee"] = "No annual fee"

            elif key == "apr":
                try:
                    apr_elem = card.find_element(By.XPATH, "//li[h3[normalize-space()='Purchase Rate']]")
                    min_apr = apr_elem.find_element(By.CSS_SELECTOR, "span[data-id^='minimumAnnualPercentageRate']").text
                    max_apr = apr_elem.find_element(By.CSS_SELECTOR, "span[data-id^='maximumAnnualPercentageRate']").text
                    db[idx]["apr"] = f"{min_apr}-{max_apr}"
                except:
                    try:
                        flat = card.find_element(By.CSS_SELECTOR, "span[data-id^='annualPercentageRateSame']").text
                        db[idx]["apr"] = flat
                    except:
                        db[idx]["apr"] = "$0"

# ───────────── Uncheck boxes ─────────────

def uncheck_selected(driver, group_names):
    driver.get("https://www.citi.com/credit-cards/compare/view-all-credit-cards?vac=CONTROL")
    time.sleep(1)
    checkboxes = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[type="checkbox"]'))
    )
    for name in group_names:
        cb = next((cb for cb in checkboxes if cb.is_displayed() and cb.get_attribute("aria-label") and
                   re.sub(r"^Compare \(\d+\/3\)\s*", "", cb.get_attribute("aria-label")).strip() == name), None)
        if cb and cb.is_selected():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb)
            cb.click()
        time.sleep(2)

# ───────────── Main ─────────────

def main():
    driver = setup_driver()
    processed = set()
    db = [{"name": "", "bonus": "", "reward": "", "fee": "", "apr": ""} for _ in range(20)]
    round = 0

    while True:
        checkboxes = load_checkboxes(driver)
        unprocessed = get_unprocessed_checkboxes(checkboxes, processed)
        if not unprocessed:
            print("✅ All cards processed.")
            break

        group, stop = select_cards(driver, unprocessed, checkboxes, processed)
        click_compare(driver)
        scrape_results(driver, db, round, len(group))
        if stop:
            print("✅ Final group processed.")
            break
        uncheck_selected(driver, group)
        processed.update(group)
        round += len(group)

    driver.quit()
    for i, card in enumerate(db):
        print(card['name'])
    return db

if __name__ == "__main__":
    db = main()
