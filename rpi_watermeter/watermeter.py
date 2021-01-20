import argparse
import logging
import math
import numpy
from numpy.fft import fft, ifft
import time

from . import sensor
from . import database

logger = logging.getLogger(__name__)

class Settings():
    def __init__(self, db_host, db_org, db_token, bucket_name, raw_bucket_name=None):
        self.db_host = db_host
        self.db_org = db_org
        self.db_token = db_token
        self.bucket_name = bucket_name
        self.raw_bucket_name = raw_bucket_name

class RateInfo():
    def __init__(self, max_samples=200, compare_count=10):
        self.x = []
        self.y = []
        self.z = []
        self.max_samples = max_samples
        self.compare_count = compare_count


    def calculate_rate(self, axis):
        if len(self.x) < self.max_samples:
            return 0

        if axis == "x":
            return self._calc_rate(self.x)
        elif axis == "y":
            return self._calc_rate(self.y)
        elif axis == "z":
            return self._calc_rate(self.z)

        return 0

    @staticmethod
    def _calc_rate(data):
        logger.debug("Calclating Rate")

        #fftx = fft(data)
        #logger.debug("FFT: %s", fftx)

        res = numpy.correlate(data, data, "full")
        logger.debug("RateInfo %s", res)

        """
        def xcorr(x):
            l = 2 ** int(np.log2(x.shape[1] * 2 - 1))
            fftx = fft(x, n = l, axis = 1)
            ret = ifft(fftx * np.conjugate(fftx), axis = 1)
            ret = fftshift(ret, axes=1)
            return ret
        """
        return float(max(res))

    # TODO:  Calculate rate
    @staticmethod
    def autocorr(x, t=1):
        return numpy.correlate(numpy.array([x[:-t], x[t:]]))


    def addReading(self, x, y, z):
        self.x.append(x)
        self.y.append(y)
        self.z.append(z)
        if len(self.x) > self.max_samples:
            self.x = self.x[1:]
            self.y = self.y[1:]
            self.z = self.z[1:]

def run(settings: Settings):
    logger.info("Starting watermeter")
    meter_sensor = sensor.WaterMeterSensor()
    db = database.DatabaseV1_6(host=settings.db_host)
    db.create_database(settings.raw_bucket_name)
    db.create_database(settings.bucket_name)

    while not meter_sensor.is_ready():
        logger.warning("Waiting for the sensor to be ready")
        meter_sensor.sensor_status()
        time.sleep(1)

    rate_info = RateInfo(max_samples=5)

    logger.info("Starting to read data")
    while True:
        x, y, z = meter_sensor.get_reading()

        rate_info.addReading(x, y, z)

        if settings.raw_bucket_name is not None:
            raw_data = {
            "x": x,
            "y": y,
            "z": z,
            #"power": math.sqrt((x ** 2) + (y ** 2) + (z ** 2))
            }
            db.writeData(database=settings.raw_bucket_name, name="raw_water_sensor_data", data=raw_data)


            data = {
            "rate_fx": float(rate_info.calculate_rate("x")),
            "rate_fy": float(rate_info.calculate_rate("y")),
            "rate_fz": float(rate_info.calculate_rate("z")),
            #"power": math.sqrt((x ** 2) + (y ** 2) + (z ** 2))
            }
            db.writeData(database=settings.raw_bucket_name, name="rate_water_sensor_data", data=data)

        rate = calculate_rate(data)
        if rate > 0:
            db.writeData(database=settings.bucket_name, name="water", data={"flow": rate})


def calculate_rate(data):
    return 0
