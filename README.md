# Tapo P110 to InfluxDB via Telegraf exporter

These scripts are geared for UK users of the [Tapo P110](https://www.tapo.com/uk/product/smart-plug/tapo-p110/).

## The scripts
* `exporter.py` is the script called by Telegraf. It makes a connection to all of the configured Tapo P110 devices on the network and gets and processes their data.
    * The configuration for this script lives inside the script itself and is in YAML format. See script contents for example config.
* `price_per_kwh.py` is an optional script, also called by Telegraf. It scapes the Ofgem website for the price per kWh and standing charge values of the default standard variable tariff.
* `dashboard.json` is my dashboard, exported to be used as a template. All queries are written in the [Flux](https://docs.influxdata.com/influxdb/v2/query-data/flux/) query language.


## Installing
* On the machine running Telegraf either;
    * `pip install -r requirements.txt` or,
    * Create a virtual environemt `python3 -m venv .venv` and then install the requirements in to the venv.
* Configure the exporter script within the script itself
* Configure Telegraf to run the exporter script, setting it's data format as influx
```
[[inputs.exec]]
  commands = ["/path/to/exporter.py"]
  timeout = "10s"
  interval = "10s"
  data_format = "influx
```
* Configure Telegraf to run the price_per_kwh script
```
[[inputs.exec]]
  commands = ["/path/to/price_per_kwh.py"]
  timeout = "30s"
  interval = "24h"
  data_format = "influx"
```
* Restart Telegraf
