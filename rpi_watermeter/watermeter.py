import argparse
import logging
import math
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

def run(settings: Settings):
    logger.info("Starting watermeter")
    meter_sensor = sensor.WaterMeterSensor()
    db = database.Database(host=settings.db_host, org=settings.db_org, token=settings.db_token)

    while not meter_sensor.is_ready():
        logger.warning("Waiting for the sensor to be ready")
        meter_sensor.sensor_status()
        time.sleep(1)

    logger.info("Starting to read data")
    while True:
        x, y, z = meter_sensor.get_reading()
        data = {
        "x": x,
        "y": y,
        "z": z,
        "power": math.sqrt((x ** 2) + (y ** 2) + (z ** 2))
        }
        if settings.raw_bucket_name is not None:
            db.writeData(bucket=settings.raw_bucket_name, name="raw_water_sensor_data", data=data)

        rate = calculate_rate(data)
        if rate > 0:
            db.writeData(bucket=settings.bucket_name, name="water", data={"flow": rate})


def calculate_rate(data):
    # TODO:  Calculate rate
    return 0