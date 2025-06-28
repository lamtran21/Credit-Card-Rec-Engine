import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_experimental_option("prefs", {
        "profile.managed_content_settings.images": 2  # Disable image loading
    })
    return webdriver.Chrome(options=options)


def expand_all_show_more(driver):
    try:
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//button[contains(@aria-label, 'Show More Benefits')]")
            )
        )
        for button in buttons:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(0.3)
    except:
        pass  # No buttons or already expanded


def extract_card_data(card, driver):
    data = {key: "" for key in ["name", "bonus", "reward", "fee", "apr"]}

    # Name
    data["name"] = card.find_element(By.CSS_SELECTOR, "span.pad-1-r").text

    # Fee
    try:
        data["fee"] = card.find_element(
            By.CSS_SELECTOR, "p.hidden-sm-down.dls-gray-06.body-3 > span"
        ).text[2:]
    except:
        try:
            data["fee"] = card.find_element(
                By.CSS_SELECTOR, "p.hidden-sm-down.dls-gray-06.body-3 > strong"
            ).text
        except:
            data["fee"] = "N/A"

    # Rewards
    rewards = card.find_elements(By.CSS_SELECTOR, "b.dls-deep-blue")
    data["reward"] = '; '.join(r.text.strip() for r in rewards if r.text.strip())

    # Bonus / Offer
    ignore_phrases = [
        'Welcome Offer', 'Limited Time Offer', 'Apply, and if approved:',
        "Find out your offer amount", "Accept the Card with your offer"
    ]
    offers = card.find_elements(By.CSS_SELECTOR, "div._vacOfferTitle_1esd3_262 *")
    visible_texts = set()
    for offer in offers:
        if offer.tag_name == "s":
            continue
        text = offer.text.strip().replace("†", "")
        if text and not any(phrase in text for phrase in ignore_phrases):
            visible_texts.add(text)
    data["bonus"] = " ".join(visible_texts)

    # APR (opens new tab)
    try:
        original_tab = driver.current_window_handle
        link = card.find_element(By.XPATH, ".//a[@aria-label='Rates and Fees']")
        driver.execute_script("arguments[0].scrollIntoView();", link)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ".//a[@aria-label='Rates and Fees']")))
        driver.execute_script("arguments[0].click();", link)

        # Wait for and switch to the new tab
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        new_tab = [h for h in driver.window_handles if h != original_tab][0]
        driver.switch_to.window(new_tab)

        # Grab APR info
        para = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p[aria-describedby='interest-rates-rowheader-0']"))
        )
        apr = para.find_element(By.TAG_NAME, "b")
        data["apr"] = apr.text.strip()

        # Close new tab and return
        driver.close()
        driver.switch_to.window(original_tab)

    except Exception as e:
        data["apr"] = "N/A"

    return data


def scrape_amex_cards():
    driver = setup_driver()
    try:
        driver.get("https://americanexpress.com/us/credit-cards/?category=all")
        expand_all_show_more(driver)

        cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._cardTileFlexContainer_1esd3_18"))
        )

        amex_db = []
        for card in cards:
            card_data = extract_card_data(card, driver)
            amex_db.append(card_data)

        return amex_db

    finally:
        driver.quit()


def main():
    return scrape_amex_cards()

if __name__ == "__main__":
    db = main()

