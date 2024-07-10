import asyncio
import time

from tapo import ApiClient
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

hub:
  ip: 10.0.80.254
"""

cfg = safe_load(CFG)
TAPO_P110_WATTAGE = float(cfg["tapo_wattage"])
daily_energy = monthly_energy = 0


def heat_index(temp, hum):
    temp, hum = int(temp), int(hum)
    # heat-index is only fahrenheit compatible
    fahrenheit = ((temp * (9 / 5)) + 32)

    # coefficients
    T = pow(fahrenheit, 2)
    H = pow(hum, 2)
    C = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-03, -5.481717e-02, 1.22874e-03, 8.5282e-04, -1.99e-06]
    hi = C[0] + (C[1] * fahrenheit) + (C[2] * hum) + (C[3] * fahrenheit * hum) + (C[4] * T) + (C[5] * H) + (C[6] * T * hum) + (C[7] * fahrenheit * H) + (C[8] * T * H)
    # convert back to C and return
    return round((hi - 32) * (5 / 9), 2)


async def tapo_p110(device):
    global daily_energy, monthly_energy
    api_client = ApiClient(cfg.get("auth").get("user"), cfg.get("auth").get("password"))
    dev = await api_client.p110(device.get("ip"))
    res = await dev.get_energy_usage()
    data = res.to_dict()

    for k, v in data.items():
        if k == "current_power":
            data[k] += TAPO_P110_WATTAGE
        if k == "today_energy":
            data[k] += (
                TAPO_P110_WATTAGE * max(0, time.localtime().tm_hour - 1)
            ) / 1000
        if k == "month_energy":
            data[k] += (
                TAPO_P110_WATTAGE * (max(0, time.localtime().tm_mday - 1) * 24)
            ) / 1000
            data[k] += (
                TAPO_P110_WATTAGE * max(0, time.localtime().tm_hour - 1)
            ) / 1000

    daily_energy += data["today_energy"]
    monthly_energy += data["month_energy"]

    tags = ",".join([f"{k}={v}" for k, v in device.items()])
    fields = ",".join(
        [
            f"""{k}={round(v)}i"""
            for k, v in data.items()
            if k not in ("local_time",)
        ]
    )

    print(f"p110_energy_consumption,{tags} {fields}")


async def tapo_310(device):
    data = device.to_dict()
    tags = [f"name={data['nickname']}",]
    fields = [
        f"temperature={round(data['current_temp'], 2)}",
        f"humidity={data['current_humidity']}",
        f"heat_index={heat_index(data['current_temp'], data['current_humidity'])}",
        f"low_battery={1 if data['at_low_battery'] else 0}i",
        f"signal={data['signal_level']}i",
        f"online={1 if data['status'] == 'online' else 0}i",
    ]
    tags = ",".join(tags)
    fields = ",".join(fields)
    print(f"tapo_310,{tags} {fields}")


async def tapo_hub():
    loop = asyncio.get_running_loop()
    api_client = ApiClient(cfg.get("auth").get("user"), cfg.get("auth").get("password"))
    hub = await api_client.h100(cfg.get("hub").get("ip"))
    devices = await hub.get_child_device_list()
    for device in devices:
        loop.create_task(tapo_310(device))


loop = asyncio.get_event_loop()
tasks = [
    loop.create_task(tapo_p110(device)) for device in cfg.get("devices")
]
loop.run_until_complete(asyncio.wait(tasks))
loop.run_until_complete(asyncio.wait([tapo_hub(),]))
loop.close()


print(f"p110_energy_daily_total total_sum={round(daily_energy)}i")
print(f"p110_energy_monthly_total total_sum={round(monthly_energy)}i")
