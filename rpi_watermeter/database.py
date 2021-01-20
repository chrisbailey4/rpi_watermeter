from abc import ABC, abstractmethod
import datetime
import logging
import time

# For Influx DB 1.8+
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# For Influx DB before 1.8
import influxdb


logger = logging.getLogger(__name__)

class Database(ABC):
    @abstractmethod
    def connect(self):
        return NotImplemented

    @abstractmethod
    def create_database(self, database):
        return NotImplemented


    @abstractmethod
    def writeData(self, bucket, name, data, tag=None):
        return NotImplemented


class DatabaseV1_6(Database):
    def __init__(self, host, port=8086):
        self.host = host
        self.port = port
        self.client = None
        self.connect()
        if self.client is None:
            raise Exception("Failed to connect to the database")
        logger.info("Database is connected: %s", self.host)

    def connect(self):
        if self.client is None:
            try:
                logger.debug("Connecting to InfluxDB %s", self.host)
                self.client = influxdb.InfluxDBClient(host=self.host, port=self.port)
            except Exception:
                logger.exception("Faled to connect to InfluxDB %s", self.host)

    def create_database(self, database):
        self.connect()
        self.client.create_database(database)

    def writeData(self, database, name, data, tag=None):
        self.connect()

        json_body = [
            {
                "measurement": name,
                "time": time.time_ns(),
                "fields": data
                }
            ]

        self.client.write_points(json_body, database=database)





class DatabaseV2(Database):

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

    def writeData(self, database, name, data, tag=None):
        self.connect()
        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        try:
            p = Point(name)
            if tag is not None:
                p.tag(*tag)

            for key, value in data.items():
                p.field(key, value)

            logger.debug("Writing Data to DB: %s", p)
            write_api.write(bucket=database, record=p)

        except Exception:
            logger.exception("Exception writing data: %s", p)
            self.client = None
