from PyP100 import PyP110
from yaml import safe_load


CFG = """
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
for device in cfg["devices"]:
    try:
        dev = PyP110.P110(
            device["ip"], cfg["auth"]["user"], cfg["auth"]["password"]
        )
        dev.handshake()
        dev.login()
        res = dev.getEnergyUsage()

        # name=rack,
        # room=office,ip=10.0.80.2
        tags = ",".join([
            f"{k}={v}" for k, v in device.items()
        ])

        # today_runtime=711i,    # minutes
        # month_runtime=1197i,  # minutes
        # today_energy=1758i,    # watt=hours
        # month_energy=2928i,    # watt-hours
        # current_power=1526i    # watts
        fields = ",".join([
            f"{k}={v}i" for k, v in res["result"].items()
            if k not in ("local_time", "electricity_charge")
        ])
        daily_energy.append(res["result"]["today_energy"])
        monthly_energy.append(res["result"]["month_energy"])

        print(f"""p110_energy_consumption,{tags} {fields}""")
    except:
        continue

print(f"p110_energy_daily_total total_sum={sum(daily_energy)}i")
print(f"p110_energy_monthly_total total_sum={sum(monthly_energy)}i")

