import re

import requests
from bs4 import BeautifulSoup


URL = "https://www.moneysavingexpert.com/utilities/what-are-the-price-cap-unit-rates-/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    )
}
KWH_PAT = r"Unit rate: ([0-9\.]*)p per kWh"
STDC_PAT = r"Standing charge: ([0-9\.]*)p per day"

try:
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, features="html.parser")

    price_cap = soup.find(
        lambda tag: tag.name == "h2" and tag.text == "The Energy Price Cap unit rates & standing charges"
    ).find_next(
        lambda tag: tag.name == "strong" and tag.text.lower().startswith("direct debit")
    ).find_next(
        lambda tag: tag.name == "td" and tag.text == "Electricity"
    ).find_next("td").text

    kwh_res = re.search(KWH_PAT, price_cap)
    stand_chrg_res = re.search(STDC_PAT, price_cap)

    if kwh_res and stand_chrg_res:
        kwh_price, stand_chrg_price = float(kwh_res.group(1)) / 100, float(stand_chrg_res.group(1)) / 100
        print(f"p110_energy_price price_per_kwh={kwh_price},standing_charge={stand_chrg_price}")

except Exception as e:
    print(e)
    pass
