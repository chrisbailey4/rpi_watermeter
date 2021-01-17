import logging
import time
import busio
import board

import adafruit_mlx90393

logger = logging.getLogger(__name__)


class WaterMeterSensor():
    def __init__(self, i2c_bus=None):

        if i2c_bus is None:
            i2c_bus =  busio.I2C(board.SCL, board.SDA)

        self.i2c_bus = i2c_bus

        logger.debug("Connecting to Water Meter Sensor")
        self.sensor = adafruit_mlx90393.MLX90393(i2c_bus, gain=adafruit_mlx90393.GAIN_1X)


    def is_ready(self):
        logger.debug("Last status: %s", self.sensor.last_status)
        return self.sensor.last_status <= adafruit_mlx90393.STATUS_OK

    def sensor_status(self):
        self.sensor.display_status()

    def get_reading(self):
        mx, my, mz = self.sensor.magnetic

        return mx, my, mz
