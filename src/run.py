from sds011_particle_sensor.Code.sds011 import SDS011
from dotenv import load_dotenv
import os
import time


load_dotenv()
ENVIRONMENT = os.environ['ENVIRONMENT']
DEBUG = os.environ['DEBUG']
CYCLES = os.environ['CYCLES']
TIMEOUT = os.environ['TIMEOUT']
SERIAL_PATH = os.environ['SERIAL_PATH']

class Measurements:

    def __init__(self) -> None:
        self.unit = SDS011.UnitsOfMeasure.MassConcentrationEuropean
        self.sensor = SDS011(
            device_path=SERIAL_PATH,
            unit_of_measure=self.unit,
            timeout=TIMEOUT,
        )

    def get_sensor_info(self) -> None:
        print(f"""
        SDS011 Sensor Info.
        Device ID: {self.sensor.device_id}
        Device Firmware: {self.sensor.firmware}
        Current device cycle (0 is permanent on): {self.sensor.dutycycle}
        Sensor Workstate: {self.sensor.workstate}
        Sensor Report Mode: {self.sensor.reportmode}

        Number of measurements in permanent measuring mode: {CYCLES * 2}
        """)

    def _sleep_sensor(self) -> None:
        self.sensor.workstate = self.sensor.WorkStates.Sleeping

    def _take_measurements(self) -> None:
        self.sensor.reset()
        for cycle in CYCLES:
            values = self.sensor.get_values()
            if values is not None:
                self.print_values(0, values, self.unit)
    
    @staticmethod
    def print_values(timing, values, unit_of_measure):
        if unit_of_measure == SDS011.UnitsOfMeasure.MassConcentrationEuropean:
            unit = 'µg/m³'
        else:
            unit = 'pcs/0.01cft'
        print("Waited %d secs\nValues measured in %s:    PM2.5  " %
            (timing, unit), values[1], ", PM10 ", values[0])

if __name__ == "__main__":

    meas = Measurements()
    meas.get_sensor_info()
    meas._take_measurements()

    pass