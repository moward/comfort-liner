# Comfort liner

Exports data from [Honeywell Total Connect Comfort](https://www.resideo.com/us/en/total-connect-comfort-app/) thermostat to [InfluxDB](https://influxdata.com).

## Usage

Prerequisites:
- Python 3

Create a config file based on `./sample-config.json`. You should use the username and password for [https://www.mytotalconnectcomfort.com/portal](https://www.mytotalconnectcomfort.com/portal). You can get the `deviceId` from the portal by logging in and looking for a URL like `https://www.mytotalconnectcomfort.com/portal/Device/Control/<deviceId>`.

```
# Install dependencies
pip install -r requirements.txt

# Run program
python ./comfort-liner/comfort-liner.py path/to/config.json
```

## Credit

This package is heavily inspired by https://github.com/jertel/vuegraf
