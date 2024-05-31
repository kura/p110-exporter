import re
import subprocess
from datetime import datetime
from io import StringIO

import pandas
from retry import retry


URL = "https://www.moneysavingexpert.com/utilities/what-are-the-price-cap-unit-rates-/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0esr) Gecko/20000101 Firefox/124.0esr"
}
KWH_PAT = r"Unit rate: ([0-9\.]*)p per kWh"
STDC_PAT = r"Standing charge: ([0-9\.]*)p per day"

QUARTERS = {
  **dict.fromkeys([1, 2, 3], "1 january to 31 march"),
  **dict.fromkeys([4, 5, 6], "1 april to 30 june"),
  **dict.fromkeys([7, 8, 9], "1 july to 30 september"),
  **dict.fromkeys([10, 11, 12], "1 october to 31 december"),
}


@retry(Exception, tries=6, delay=10)
def get_price_cap():
    r = subprocess.run(
        ["curl", "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0esr) Gecko/20000101 Firefox/124.0esr", URL],
        capture_output=True,
        text=True
    )
    table = pandas.read_html(StringIO(r.stdout))[0]

    idx = [
        i
        for i, v in enumerate(table[0])
        if isinstance(v, str) and v.lower() == "electricity"
    ][0]

    current_quarter = QUARTERS[datetime.now().month]
    price_cap = None
    for i in range(1, len(table)):
        heading = table[i][0].lower()
        if "energy price cap" in heading and current_quarter in heading:
            price_cap = table[i][idx]
    if not price_cap:
        raise Exception("Couldn't find price cap")

    kwh_res = re.search(KWH_PAT, price_cap)
    stand_chrg_res = re.search(STDC_PAT, price_cap)

    try:
        kwh_price = float(kwh_res.group(1)) / 100
        stand_chrg_price = float(stand_chrg_res.group(1)) / 100
    except:
        raise Exception("Couldn't convert to float")

    return kwh_price, stand_chrg_price


if __name__ == "__main__":
    kwh_price, stand_chrg_price = get_price_cap()
    if kwh_price and stand_chrg_price:
        print(
            f"p110_energy_price price_per_kwh={kwh_price},"
            f"standing_charge={stand_chrg_price}"
        )
