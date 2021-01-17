import datetime
import logging

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)

class Database():
    def __init__(self, host, org, token):

        self.host = host
        self.org = org
        self.token = token

        self.client = None
        self.connect()
        if self.client is not None:
            logger.info("Database is connected: %s", self.host)


    def connect(self):
        if self.client is None:
            try:
                logger.debug("Connecting to InfluxDB %s", self.host)
                self.client = InfluxDBClient(url=self.host, token=self.token, org=self.org)
            except Exception:
                logger.exception("Faled to connect to InfluxDB %s", self.host)

    def writeData(self, bucket, name, data, tag=None):
        self.connect()

        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        try:
            p = Point(name)
            if tag is not None:
                p.tag(*tag)

            for key, value in data.items():
                p.field(key, value)

            logger.debug("Writing Data to DB: %s", p)
            write_api.write(bucket=bucket, record=p)

        except Exception:
            logger.exception("Exception writing data: %s", p)
            self.client = None
