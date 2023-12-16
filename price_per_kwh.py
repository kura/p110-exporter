import re
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

try:
    r = requests.get(URL, headers=HEADERS)
    table = pandas.read_html(StringIO(r.text))[0]

    idx = [
        i for i, v in enumerate(table[0])
        if isinstance(v, str) and v.lower() == "electricity"
    ][0]

    for i in range(1, len(table)):
        if "current energy price cap" in table[i][0].lower():
            price_cap = table[i][idx]

    kwh_res = re.search(KWH_PAT, price_cap)
    stand_chrg_res = re.search(STDC_PAT, price_cap)

    if kwh_res and stand_chrg_res:
        kwh_price, stand_chrg_price = (
            float(kwh_res.group(1)) / 100, float(stand_chrg_res.group(1)) / 100
        )
        print(
            f"p110_energy_price price_per_kwh={kwh_price},"
            f"standing_charge={stand_chrg_price}"
        )

except Exception as e:
    print(e)
    pass
