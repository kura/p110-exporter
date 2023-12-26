import re
from datetime import datetime
from io import StringIO

import pandas
import requests


URL = "https://www.moneysavingexpert.com/utilities/what-are-the-price-cap-unit-rates-/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    )
}
KWH_PAT = r"Unit rate: ([0-9\.]*)p per kWh"
STDC_PAT = r"Standing charge: ([0-9\.]*)p per day"

QUARTERS = {
  **dict.fromkeys([1, 2, 3], "1 january to 31 march"),
  **dict.fromkeys([4, 5, 6], "1 april to 30 june"),
  **dict.fromkeys([7, 8, 9], "1 july to 30 september"),
  **dict.fromkeys([10, 11, 12], "1 october to 31 december"),
}

try:
    r = requests.get(URL, headers=HEADERS)
    table = pandas.read_html(StringIO(r.text))[0]

    idx = [
        i
        for i, v in enumerate(table[0])
        if isinstance(v, str) and v.lower() == "electricity"
    ][0]

    current_quarter = QUARTERS[datetime.now().month]
    price_cap = None
    for i in range(1, len(table)):
        heading = table[i][0].lower()
        if "current energy price cap" in heading and current_quarter in heading:
            price_cap = table[i][idx]
    if not price_cap:
        raise Exception("Couldn't find price cap")

    kwh_res = re.search(KWH_PAT, price_cap)
    stand_chrg_res = re.search(STDC_PAT, price_cap)

    if kwh_res and stand_chrg_res:
        kwh_price, stand_chrg_price = (
            float(kwh_res.group(1)) / 100,
            float(stand_chrg_res.group(1)) / 100,
        )
        print(
            f"p110_energy_price price_per_kwh={kwh_price},"
            f"standing_charge={stand_chrg_price}"
        )

except Exception as e:
    pass
