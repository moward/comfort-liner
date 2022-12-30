import json
import logging
import signal
import sys
from datetime import datetime
from pprint import pprint
from threading import Event

import influxdb_client
import somecomfort
from influxdb_client.rest import ApiException

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(name)s %(message)s", level=logging.INFO)


def main():
    global running
    running = True

    if len(sys.argv) != 2:
        print("Usage: python {} <config-file>".format(sys.argv[0]))
        sys.exit(1)

    configFilename = sys.argv[1]
    config = {}
    with open(configFilename) as configFile:
        config = json.load(configFile)

    def handleExit(signum, frame):
        global running
        logger.error("Caught exit signal")
        running = False
        pauseEvent.set()

    signal.signal(signal.SIGINT, handleExit)
    signal.signal(signal.SIGHUP, handleExit)

    pauseEvent = Event()

    client = somecomfort.SomeComfort(
        config["totalConnectComfort"]["username"],
        config["totalConnectComfort"]["password"],
    )

    device: somecomfort.Device = client.get_device(
        config["totalConnectComfort"]["deviceId"]
    )

    bucket = config["influxDb"]["bucket"]

    influx2 = influxdb_client.InfluxDBClient(
        url=config["influxDb"]["url"],
        token=config["influxDb"]["token"],
        org=config["influxDb"]["org"],
        verify_ssl=config["influxDb"]["sslVerify"],
    )
    write_api = influx2.write_api(
        write_options=influxdb_client.client.write_api.SYNCHRONOUS
    )

    while running:
        timestamp = datetime.utcnow()

        device.refresh()

        data_point = (
            influxdb_client.Point("thermostat_data")
            .tag("device_name", device.name)
            .field("is_alive", device.is_alive)
            .field("fan_running", device.fan_running)
            .field("fan_mode", device.fan_mode)
            .field("system_mode", device.system_mode)
            .field("setpoint_cool", device.setpoint_cool)
            .field("setpoint_heat", device.setpoint_heat)
            .field(
                "hold_heat",
                device.hold_heat
                if type(device.hold_heat) is bool
                else str(device.hold_heat),
            )
            .field(
                "hold_cool",
                device.hold_cool
                if type(device.hold_cool) is bool
                else str(device.hold_cool),
            )
            .field("current_temperature", device.current_temperature)
            .field("equipment_output_status", device.equipment_output_status)
            .field("outdoor_temperature", device.outdoor_temperature)
            .time(time=timestamp)
        )

        logger.info(f"Writing data for {device.name} at {timestamp}")

        try:
            write_api.write(bucket, None, data_point)
        except ApiException as e:
            logger.error(f"Encountered error {e.status}: {e.reason}")

        logger.info(f"Wrote data for {device.name} at {timestamp}")

        pauseEvent.wait(config["pollInterval"])


if __name__ == "__main__":
    main()
