import time

from PyP100 import PyP110
from yaml import safe_load


CFG = """
# This is the mean power usage of my Tapo P110 itself.
# It is added to the `current_power` value for each device
# monitored.
# It is also used to add the watt-hours value to each device
# monitored.
#
# This value is in milliwatts (mW)
tapo_wattage: 1130

auth:
  user: user@example.com
  password: some_password

devices:
  - name: kettle
    room: kitchen
    ip: 10.0.80.2
  - name: pc
    room: office
    ip: 10.0.80.3
  - name: rack
    room: office
    ip: 10.0.80.4
  - name: tv
    room: living_room
    ip: 10.0.80.5
"""

daily_energy = []
monthly_energy = []

cfg = safe_load(CFG)
TAPO_P110_WATTAGE = float(cfg["tapo_wattage"])
for device in cfg["devices"]:
    dev = PyP110.P110(device["ip"], cfg["auth"]["user"], cfg["auth"]["password"])

    res = dev.getEnergyUsage()

    try:
        # name=rack,
        # room=office,
        # ip=10.0.80.2
        tags = ",".join([f"{k}={v}" for k, v in device.items()])

        for k, v in res.items():
            if k == "current_power":
                res[k] += TAPO_P110_WATTAGE
            if k == "today_energy":
                res[k] += (
                    TAPO_P110_WATTAGE * max(0, time.localtime().tm_hour - 1)
                ) / 1000
            if k == "month_energy":
                res[k] += (
                    TAPO_P110_WATTAGE * (max(0, time.localtime().tm_mday - 1) * 24)
                ) / 1000
                res[k] += (
                    TAPO_P110_WATTAGE * max(0, time.localtime().tm_hour - 1)
                ) / 1000

        # today_runtime=711i,   # minutes
        # month_runtime=1197i,  # minutes
        # today_energy=1758,    # watt-hours (Wh)
        # month_energy=2928,    # watt-hours (Wh)
        # current_power=1526    # milliwatts (mW)
        fields = ",".join(
            [
                f"""{k}={round(v)}i"""
                for k, v in res.items()
                if k not in ("local_time", "electricity_charge")
            ]
        )
        daily_energy.append(res["today_energy"])
        monthly_energy.append(res["month_energy"])

        print(f"""p110_energy_consumption,{tags} {fields}""")
    except Exception as e:
        continue

print(f"p110_energy_daily_total total_sum={round(sum(daily_energy))}i")
print(f"p110_energy_monthly_total total_sum={round(sum(monthly_energy))}i")
