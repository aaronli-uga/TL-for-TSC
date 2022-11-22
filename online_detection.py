'''
Author: Qi7
Date: 2022-11-22 10:32:35
LastEditors: aaronli-uga ql61608@uga.edu
LastEditTime: 2022-11-22 11:53:48
Description: 
'''
import pandas as pd 
from influxdb import InfluxDBClient
from prophet import Prophet
import time, datetime
import pytz
import warnings
import matplotlib.pyplot as plt
from random import randint

warnings.filterwarnings("ignore")

time_format = "%Y-%m-%d %H:%M:%S"
tz_NY = pytz.timezone("America/New_York")

#influxDB database config
host = "sensorwebdata.engr.uga.edu"
username = "test"
pwd = "sensorweb"
dbName = "synthetic_testbed" # Database name in InfluxDB
port = 8086
measurement = "Voltage"  # Table name in InfluxDB
detection_measurement = "Detection"
tag = "sensor_1" # Tag name of your data, could have multiple tags
isSSL = True

client = InfluxDBClient(
    host=host, port=port, username=username, password=pwd, database=dbName, ssl=isSSL
)

# define the reading time range of datebase
query_window_size = 20 # query window size is 20 seconds

while True:
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(seconds=20)

    start_timestamp = start_time.timestamp()
    start_str = str(int((start_timestamp) * 1000000000))

    end_timestamp = end_time.timestamp()
    end_str = str(int((end_timestamp) * 1000000000))

    readQuery = (
        "SELECT * FROM "
        + measurement
        + " WHERE time > "
        + start_str
        + " and time < "
        + end_str
    )



    result = client.query(readQuery)
    values = result.get_points()

    t_col = []
    value_col = []
    for point in values:
        t_col.append(point["time"])
        value_col.append(point["value"])

    # fig, (ax1) = plt.subplots(1, 1,figsize=(10,5))
    # fig.suptitle('Live data reading')
    # ax1.plot(value_col)
    # ax1.set_title("live data")
    # plt.show()

    # string format for the timestamp
    for i in range(len(t_col)):
        temp = t_col[i].split('T')
        t_col[i] = temp[0] + ' ' + temp[1].split('Z')[0]

    lists = [t_col, value_col]
    df = pd.DataFrame(lists).T
    df.columns = ['ds', 'y']
    
    isAnomly = randint(0, 1)

    writeData = [
        {
        "measurement": detection_measurement,
        "tags": {"location": tag},
        "fields": {
            "value": isAnomly
        },
        "time": int(end_timestamp)  #change to the 
        }
    ]

    client.write_points(
        writeData, time_precision="s", batch_size=10, protocol="json"
    )

    time.sleep(query_window_size * 0.8)