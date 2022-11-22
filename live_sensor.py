'''
Author: Qi7
Date: 2022-11-21 10:25:15
LastEditors: aaronli-uga ql61608@uga.edu
LastEditTime: 2022-11-22 10:30:09
Description: 
'''
import warnings
from influxdb import InfluxDBClient
import datetime, time
import pytz
# import libraries for generating signals
import utils.sequences
from utils.sequences import generate_random_kwargs
from utils.sequences import UpAndDown, StraightLine, HighPeak, Up, Down, UpAndDown, UpAndDownAndNormal, CrazyRandom, SinWave
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored
import os

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
tag = "sensor_1" # Tag name of your data, could have multiple tags
isSSL = True

client = InfluxDBClient(
    host=host, port=port, username=username, password=pwd, database=dbName, ssl=isSSL
)

#%% Example for generating some sinewave data / peak data
fs = 1 #Hz
# what the time series sequence length will be
seq_lengths = 100
# How many samples to generate
num_samples = 1

# number of cycles we want our segment pattern to repeat itself
num_cycles = 3
# How much std or noise we want to add to the time series
std = 0
# a start and end range for the starting point of the time series
starting_point = [-1, 1]
# starting_point = 0

# to what value we would like to normalized the final time series
y_max_value = [-2, 2]
# y_max_value = 2

kwargs = {
    'num_samples': num_samples,
    'seq_length': seq_lengths,
    'num_cycles': num_cycles,
    'std': std,
    'starting_point': starting_point,
    'y_max_value': y_max_value
}

signal_pattern = SinWave

# %%
# Specify a start time or current time
#startTime = datetime.datetime(2022, 11, 9, 14, 50, 0, 0, tz_NY)
startTime = datetime.datetime.now(tz_NY)
time_interval = 1 / fs
# timestamp = [startTime.timestamp()]
# for _ in range(len(UTS.flatten() - 1)):
#     timestamp.append(timestamp[-1] + time_interval)

# UTS = HighPeak(**kwargs).generate_data()
# UTS = UTS.flatten()

timestamp = startTime.timestamp()

while True:
    UTS = signal_pattern(**kwargs).generate_data()
    # fig, (ax1) = plt.subplots(1, 1,figsize=(10,5))
    # fig.suptitle('UpAndDown two samples')
    # ax1.plot(UTS[0])
    # ax1.set_title("Generated UTS")
    # plt.show()
    UTS = UTS.flatten()
    for i in range(len(UTS)):
        writeData = [
            {
            "measurement": measurement,
            "tags": {"location": tag},
            "fields": {
                "package number": UTS[i]
            },
            "time": int(timestamp * 1)  #change to the 
            }
        ]
        timestamp += time_interval

        client.write_points(
            writeData, time_precision="s", batch_size=10, protocol="json"
        )
        # client.write_points(
        #     writeData, batch_size=10, protocol="json"
        # )
        time.sleep(time_interval)
        # print(timestamp)
# %%
