import serial, struct, sys, time, json, subprocess
from dotenv import load_dotenv
import os

class AirQualitySensor:
    def __init__(self) -> None:
        self.ser = None
        self.sleep_s = 1
        load_dotenv()
        self.DEBUG = os.getenv("DEBUG")
        CMD_MODE = os.getenv("CMD_MODE")
        CMD_QUERY_DATA = os.getenv("CMD_QUERY_DATA")
        CMD_DEVICE_ID = os.getenv("CMD_DEVICE_ID")
        self.CMD_SLEEP = os.getenv("CMD_SLEEP")
        CMD_FIRMWARE = os.getenv("CMD_FIRMWARE")
        CMD_WORKING_PERIOD = os.getenv("CMD_WORKING_PERIOD")
        MODE_ACTIVE = os.getenv("MODE_ACTIVE")
        MODE_QUERY = os.getenv("MODE_QUERY")
        PERIOD_CONTINUOUS = os.getenv("PERIOD_CONTINUOUS")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def _initiate_serializer(self):
        """
        Initiate connection to USB serial port.
        """
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyUSB0"
        self.ser.baudrate = 9600  # speed of communication over channel
        self.ser.open()
        self.ser.flushInput()

    def cmd_set_sleep(self):
        self.ser.write(self.construct_command([0x1, 1]))
        response = self.read_response()

    def read_response(self):
        byte = 0
        while byte != "\xaa":
            byte = self.ser.read(size=1)

        d = self.ser.read(size=9)

        if self.DEBUG:
            self.dump(d, '< ')
        return byte + d

    def construct_command(self, cmd, data=[]):
        assert len(data) <= 12
        data += [0,]*(12-len(data))
        checksum = (sum(data)+self.CMD_SLEEP-2)%256
        ret = "\xaa\xb4" + chr(self.CMD_SLEEP)
        ret += ''.join(chr(x) for x in data)
        ret += "\xff\xff" + chr(checksum) + "\xab"

        if self.DEBUG:
            self.dump(ret, '> ')
        return ret

    def dump(d, prefix=''):
        print(prefix + ' '.join(x.encode('hex') for x in d))

if __name__ == "__main__":
    with AirQualitySensor() as aqi:
        print(dir(aqi.ser))
        aqi.cmd_set_sleep()
    