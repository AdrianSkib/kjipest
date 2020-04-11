import datetime
import pandas as pd
from server import *

x = datetime.date.today()
# print(x)
xx = datetime.datetime.strptime("2020-04-08", "%Y-%m-%d").date()
d = {"location": "Malvik",
    "temperature": [1],
    "windDirection": [1],
    "windSpeed": [1],
    "windGust": [1],
    "humidity": [1],
    "pressure": [1],
    "cloudiness": [1],
    "fog": [1],
    "lowClouds": [1],
    "mediumClouds": [1],
    "highClouds": [1],
    "dewpointTemperature": [1]}
df = pd.DataFrame(d)
# print(xx)
collection = connect_to_server()
update_all_locations(df,collection)