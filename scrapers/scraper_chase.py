import re
import requests
from bs4 import BeautifulSoup

def scrape_chase_cards():
    # _______Load Chase Page_______
    url = 'https://creditcards.chase.com/all-credit-cards?iCELL=61GN'
    headers = {'User-Agent': 'MOZILLA/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # _______Extract w Beautiful Soup_______
    card_containers = soup.find_all('div', class_='cmp-cardsummary__inner-container')

    chase_db = [{} for _ in range(len(card_containers))]
    required_keys = ["name", "bonus", "reward", "fee", "apr"]
    for card in chase_db:
        for key in required_keys:
            card.setdefault(key, "")

    for i, card in enumerate(card_containers):
        # Extract card title
        title_tag = card.find('div', class_='cmp-cardsummary__inner-container__title')
        title_text = title_tag.get_text()
        if title_tag:
            if re.search(r"Business", title_text):
                continue #do not get business cards, only personal cards
            match = re.search(r"^\n*\s*(.*?)\s*(?:(?:Credit Card|Card)\s+)?Links to product page", title_text)
            card_name = re.sub(r"[^a-zA-Z0-9\s]", "", match.group(1)).strip() if match else 'N/A'
            chase_db[i]['name'] = card_name

        # Extract details
        glance_div = card.find('div', class_='cmp-cardsummary__inner-container--glance')
        glance_text = glance_div.get_text().strip().replace("AT A GLANCE", "") if glance_div else 'N/A'
        chase_db[i]['reward'] = glance_text

        # Extract offer summary
        offer_div = card.find('div', class_='cmp-cardsummary__inner-container--card-member-offer')
        offer_text = offer_div.get_text(strip=True).replace("NEW CARDMEMBER OFFER", "") if offer_div else 'N/A'
        chase_db[i]['offer'] = offer_text

        # Extract APR
        apr_div = card.find('div', class_='cmp-cardsummary__inner-container--purchase-apr')
        if apr_div:
            apr_values = apr_div.find_all('span', class_='apr-value')
            apr = '-'.join([v.get_text(strip=True) for v in apr_values])
        else:
            apr = '$0'
        chase_db[i]['apr'] = apr

        # Extract Annual Fee
        fee_div = card.find('div', class_='cmp-cardsummary__inner-container--annual-fee')
        fee_text = fee_div.get_text()
        if fee_div:
            match = re.search(r'\$\d+(\.\d{1,2})?', fee_text) #get numbers only
            fee_text = match.group(0) if match else 'N/A'
        chase_db[i]['fee'] = fee_text

    return chase_db

def main():
    return scrape_chase_cards()

if __name__ == "__main__":
    db = main()

