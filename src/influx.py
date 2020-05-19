from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

API_KEY = f = open('../creds/influx.token').read()[:-1]
bucket = "test"
org = "05a92510f9f10000"
url = "http://localhost:9999"

client = InfluxDBClient(url=url, token=API_KEY)
write_api = client.write_api(write_options=SYNCHRONOUS)

lines = []
f = open("../output/chronograf.txt")
for l in f:
    lines.append(l)

write_api.write(bucket, org, lines)
