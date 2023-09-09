import re

import requests
from bs4 import BeautifulSoup


KWH_PAT = r"([0-9\.]*) per kWh"
STDC_PAT = r"([0-9\.]*) daily standing"
try:
    r = requests.get("https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap")
    soup = BeautifulSoup(r.text, features="html.parser")
    kwh_text = soup.find_all("table")[1].find(lambda tag: tag.name == "p" and "per kWh" in tag.text).text
    kwh_res = re.search(KWH_PAT, kwh_text)
    stand_chrg_text = soup.find_all("table")[1].find(lambda tag: tag.name == "p" and "daily standing charge" in tag.text).text
    stand_chrg_res = re.search(STDC_PAT, stand_chrg_text)
    if kwh_res and stand_chrg_res:
        print(f"p110_energy_price price_per_kwh={kwh_res.group(1)},standing_charge={stand_chrg_res.group(1)}")

except Exception:
    pass
