from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

API_KEY = "QcNRDI-5FB45PTPo431Lhqz3Zo0P2u4Du0Uye1yVRdTFFkXNWjfgbm-rMizJc_Pw0KCfpH7Df5_SOcAH7-UX0g=="
host = "https://us-west-2-1.aws.cloud2.influxdata.com"
bucket = "my-bucket"


client = InfluxDBClient(url="https://us-west-2-1.aws.cloud2.influxdata.com", token=API_KEY)
write_api = client.write_api(write_options=SYNCHRONOUS)
