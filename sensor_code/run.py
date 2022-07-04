from multiprocessing import AuthenticationError
from sds011_particle_sensor.Code.sds011 import SDS011
from dotenv import load_dotenv
import os
import time
from pathlib import Path

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


class Measurements:
    """
    Main orchestration class to take measurements from SDS011 sensor.
    Wraps existing SDS011 codebase for my specific use case, code taken
    with thanks from
    https://github.com/chrisballinger/sds011_particle_sensor.
    """

    def __init__(
            self,
            serial_path: str,
            cassandra_client_id: str,
            cassandra_client_secret: str,
            cassandra_config_fp: str) -> None:

        self.serial_path = serial_path
        self.unit = SDS011.UnitsOfMeasure.MassConcentrationEuropean
        self.sensor = SDS011(
            device_path=self.serial_path,
            unit_of_measure=self.unit,
        )

        # overwritten each time measurement is taken
        self.latest_measurement = None
        self.data_to_write = None

        self.take_continuous_meas = True

        self.cassandra_client_id = cassandra_client_id
        self.cassandra_client_secret = cassandra_client_secret
        self.cassandra_config_fp = Path(cassandra_config_fp)
        self._cassandra_auth()

    def _cassandra_auth(self) -> None:
        cloud_config = {'secure_connect_bundle': self.cassandra_config_fp}
        auth_provider = PlainTextAuthProvider(
            self.cassandra_client_id, self.cassandra_client_secret)
        self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        self.session = self.cluster.connect("air_quality_data")
        row = self.session.execute("select release_version from system.local").one()
        if row:
            print(row[0])
        else:
            raise AuthenticationError("Failed to auth to cassandra db")

    def _write_to_cassandra(self) -> None:
        query_str = """
        INSERT INTO air_quality_data.measurements (timestamp, pm2_5, pm10, unit)
        VALUES (%s, %s, %s, %s)
        """

        self.session.execute(
            query_str,
            (
                int(self.data_to_write["timestamp_unix"]),
                round(float(self.data_to_write["pm2.5"]), 2),
                round(float(self.data_to_write["pm10"]), 2),
                str(self.data_to_write["unit"])
            )
        )

    def print_sensor_info(self) -> None:
        print(f"""
        SDS011 Sensor Info.
        Device ID: {self.sensor.device_id}
        Device Firmware: {self.sensor.firmware}
        Current device cycle (0 is permanent on): {self.sensor.dutycycle}
        Sensor Workstate: {self.sensor.workstate}
        Sensor Report Mode: {self.sensor.reportmode}
        """)

    def _sleep_sensor(self) -> None:
        self.sensor.workstate = self.sensor.WorkStates.Sleeping

    def _unsleep_sensor(self) -> None:
        self.sensor.workstate = self.sensor.WorkStates.Measuring

    def _take_measurements(self) -> None:
        print("reset sensor and wait 60s for warmup")
        self.sensor.reset()
        time.sleep(60)
        self.print_sensor_info()
        print("taking measurement")
        self.latest_measurement = self.sensor.get_values()
        if self.latest_measurement is not None:
            self.print_values(
                timing=0,
                values=self.latest_measurement,
                unit_of_measure=self.unit
            )
        print("writing measurement to cassandra")
        self._parse_measurements()
        self._write_to_cassandra()
        self._sleep_sensor()

    def _parse_measurements(self) -> None:

        if self.unit == SDS011.UnitsOfMeasure.MassConcentrationEuropean:
            unit = 'µg/m³'
        else:
            unit = 'pcs/0.01cft'
        self.data_to_write = {
             "timestamp_unix": time.time(),
             "pm2.5": self.latest_measurement[1],
             "pm10": self.latest_measurement[0],
             "unit": unit
         }

    def _upload_measurements_to_cassandra(self) -> None:
        pass

    @staticmethod
    def print_values(timing, values, unit_of_measure):
        if unit_of_measure == SDS011.UnitsOfMeasure.MassConcentrationEuropean:
            unit = 'µg/m³'
        else:
            unit = 'pcs/0.01cft'
        print("Waited %d secs\nValues measured in %s:    PM2.5  " %
             (timing, unit), values[1], ", PM10 ", values[0])


if __name__ == "__main__":
    load_dotenv()
    ENVIRONMENT = str(os.environ['ENVIRONMENT'])
    CASSANDRA_CLIENT_ID = os.environ['CASSANDRA_CLIENT_ID']
    CASSANDRA_CLIENT_SECRET = os.environ['CASSANDRA_CLIENT_SECRET']
    CASSANDRA_CONFIG_FP = os.environ['CASSANDRA_CONFIG_FP']
    SERIAL_PATH = str(os.environ['SERIAL_PATH'])
    meas = Measurements(
        serial_path=SERIAL_PATH,
        cassandra_client_id=CASSANDRA_CLIENT_ID,
        cassandra_client_secret=CASSANDRA_CLIENT_SECRET,
        cassandra_config_fp=CASSANDRA_CONFIG_FP)
    meas._take_measurements()

    pass
