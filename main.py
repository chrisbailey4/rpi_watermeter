import argparse
import os
import logging
import sys

from rpi_watermeter import watermeter

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s %(message)s"
LOG_FORMAT_VERBOSE = "%(asctime)s [%(levelname)s] %(name)s %(filename)s.%(lineno)d %(message)s"

CONFIG_FILE = ".watermeter.conf"

if __name__ == "__main__":
    parser = argparse.ArgumentParser("watermeter app", fromfile_prefix_chars='@')
    parser.add_argument('--db-host', required=True, help="InfluxDB Hostname & port")
    parser.add_argument('--db-token', required=True, help="InfluxDB token for access")
    parser.add_argument('--db-org', help="InfluxDB token for access", default="watermeter")
    parser.add_argument('--db-bucket', help="InfluxDB Bucket name for the flow data", default="watermeter")
    parser.add_argument('--db-raw-bucket', help="InfluxDB bucket name for raw data.  If not specified, no raw data is logged")

    parser.add_argument('-v', '--verbose', action='count', default=0)

    argv = sys.argv[1:]
    if os.path.exists(CONFIG_FILE):
        argv = ['@%s' % CONFIG_FILE] + argv

    args = parser.parse_args(argv)

    log_level = logging.INFO
    log_format = LOG_FORMAT
    if args.verbose > 0:
        log_level = logging.DEBUG
    if args.verbose > 1:
        log_format = LOG_FORMAT_VERBOSE


    logging.basicConfig(format=log_format, level=log_level)

    settings = watermeter.Settings(
        db_host=args.db_host,
        db_org=args.db_org,
        db_token=args.db_token,
        bucket_name=args.db_bucket,
    )
    if args.db_raw_bucket:
        settings.raw_bucket_name = args.db_raw_bucket

    watermeter.run(settings=settings)



