# coding=utf-8
import pymongo
import pandas as pd
import datetime
import numpy as np
import math
from meteocalc import Temp, feels_like
import matplotlib.pyplot as plt


shortTermWindowSize = 96 # Since there are 96 15-minutes a day and we want short term window of a day
longTermWindowSize = shortTermWindowSize*30 # Long term window of a month. 
# You should be able to adjust to a lot of weather variance after a month of it.

# Sets up connection to server and returns the collection containing weather data for all locations.
# @Todo: Add authentication (preddy easy)
def connect_to_db():
  kjipestDBClient = pymongo.MongoClient("mongodb://localhost:27017/")
  kjipestDB = kjipestDBClient["KjipestDB"]
  collection = kjipestDB["Locations"]
  return collection

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def movingMean(newMeasurement, oldMean):
  newMeasurement = float(newMeasurement)
  oldMean = float(oldMean)
  return oldMean + (newMeasurement-oldMean)/(shortTermWindowSize+1)

def newMean(oldData,row,field):
  return movingMean(row[field],oldData["mean"][field])

def movingVar(oldVar,oldMean,newMean,newMeasurement,shortTerm):
  oldVar = float(oldVar)
  oldMean = float(oldMean)
  newMean = float(newMean)
  newMeasurement = float(newMeasurement)
  if shortTerm:
    # return oldVar + oldMean*oldMean - newMean*newMean + (newMeasurement*newMeasurement - oldVar - oldMean*oldMean)/(shortTermWindowSize+1)
    return oldVar + ((newMeasurement - oldMean)*(newMeasurement - oldMean) - oldVar)/(shortTermWindowSize+1)
  else:
    return oldVar + ((newMeasurement - oldMean)*(newMeasurement - oldMean) - oldVar)/(longTermWindowSize+1)
    # return oldVar + oldMean*oldMean - newMean*newMean + (newMeasurement*newMeasurement - oldVar - oldMean*oldMean)/(longTermWindowSize+1)

def newVariance(oldData,row,field,shortTerm,values):
  return movingVar(oldData["var"][field],oldData["mean"][field],values["$set"]["mean"][field],row[field],shortTerm)

# 
def calcTempKjiphet(effTemp):
  if effTemp > 35:
    diff = abs(35 - effTemp)
    a = float(3)/5
    b = 1
  if effTemp > 30 and effTemp <= 35:
    diff = abs(30 - effTemp)
    a = float(1)/5
    b = 0
  if effTemp > 5 and effTemp <= 30:
    diff = abs(30 - effTemp)
    a = float(2)/25
    b = 0
  if effTemp > -10 and effTemp <= 5:
    diff = abs(5 - effTemp)
    a = float(2)/15
    b = 2
  if effTemp <= -10:
    diff = abs(-10 - effTemp)
    a = float(4)/15
    b = 4
  return a*diff + b

# Fog is worst, then low clouds, medium clouds and finally high clouds. Picks the one with highest percentage and calcs based on that.
def calcCloudKjiphet(fog, low, med, hi):
  maxCloud = max(fog,low,med,hi)
  if fog == maxCloud:
    return float(8)/100*fog
  if low == maxCloud:
    return float(6)/100*fog
  if med == maxCloud:
    return float(4)/100*med
  else: 
    return float(2)/100*med

# Calculates the kjiphet of a location. 8 is almost max of sigmoid, so take max value of something and divide by 8 to get constant.
def kjiphet(data):
  # Get effective temperature
  temp = Temp(float(data["values"]["temperature"]),"c")
  windSpeed = 2.23694*float(data["values"]["humidity"])
  humidity = float(data["values"]["humidity"])
  effTemp = feels_like(temperature=temp, humidity=humidity, wind_speed=windSpeed).c
  # Calc temperature kjiphet
  tempKjiphet = calcTempKjiphet(effTemp)
  # 20 m/s is max wind speed ish, everything above is about the same 
  windKjiphet = float(8)/20*float(data["values"]["windSpeed"])
  # gust of that are more than 10 m/s more than the wind speed really sucks (Does gust value work like this?)
  gust = float(data["values"]["windGust"])
  gustKjiphet = 0
  if gust > 0:
    gustKjiphet = float(10)/8*(gust - float(data["values"]["windSpeed"]))
  cloudKjiphet = calcCloudKjiphet(float(data["values"]["fog"]),float(data["values"]["lowClouds"]),float(data["values"]["mediumClouds"]),float(data["values"]["highClouds"]))
  # precipitation is mm/minute I believe, so the max value recorded in Norway is 4.3, normal amount seems to be under 1
  precKjiphet = 2*float(data["values"]["precipitation"])
  # Variance kjiphet still not implemented
  # varianceKjiphet = 0
  # Interplay kjiphet not implemented
  # interplayKjiphet = 0 # Typ drizzle er chill når det er horevarmt, regn er ekstra kjipt når det temp nær
  # Weight the different kjiphet's, summing weights to 1
  return 100*sigmoid(0.40*tempKjiphet + 0.10*gustKjiphet + 0.10*cloudKjiphet + 0.20*precKjiphet) 

# Inserts data from one location into database.
def update_location(row, collection):
  # Get old data
  query = { "location": row["location"]}
  oldDataStruct = collection.find(query)
  firstUpdate = True
  values = {"$set": {"values": {"temperature":  row["temperature"],
                                  "windDirection": row["windDirection"],
                                  "windSpeed": row["windSpeed"],
                                  "windGust": row["windGust"],
                                  "humidity": row["humidity"],
                                  "pressure": row["pressure"],
                                  "cloudiness": row["cloudiness"],
                                  "fog": row["fog"],
                                  "lowClouds": row["lowClouds"],
                                  "mediumClouds": row["mediumClouds"],
                                  "highClouds": row["highClouds"],
                                  "dewpointTemperature": row["dewpointTemperature"],
                                  "precipitation": row["precipitation"]},
                      "prec_type": row["prec_type"],
                      "lat": row["lat"],
                      "lon": row["lon"]}}
  for oldData in oldDataStruct:
    firstUpdate = False
    values["$set"]["mean"]=      {"temperature":  newMean(oldData,row,"temperature"),
                                  "windDirection": newMean(oldData,row,"windDirection"),
                                  "windSpeed": newMean(oldData,row,"windSpeed"),
                                  "windGust": newMean(oldData,row,"windGust"),
                                  "humidity": newMean(oldData,row,"humidity"),
                                  "pressure": newMean(oldData,row,"pressure"),
                                  "cloudiness": newMean(oldData,row,"cloudiness"),
                                  "fog": newMean(oldData,row,"fog"),
                                  "lowClouds": newMean(oldData,row,"lowClouds"),
                                  "mediumClouds": newMean(oldData,row,"mediumClouds"),
                                  "highClouds": newMean(oldData,row,"highClouds"),
                                  "dewpointTemperature": newMean(oldData,row,"dewpointTemperature"),
                                  "precipitation": newMean(oldData,row,"precipitation")}
    values["$set"]["var"]=        {"temperature": newVariance(oldData,row,"temperature",False,values),
                                  "windDirection": newVariance(oldData,row,"windDirection",False,values),
                                  "windSpeed": newVariance(oldData,row,"windSpeed",False,values),
                                  "windGust": newVariance(oldData,row,"windGust",False,values),
                                  "humidity": newVariance(oldData,row,"humidity",False,values),
                                  "pressure": newVariance(oldData,row,"pressure",False,values),
                                  "cloudiness": newVariance(oldData,row,"cloudiness",False,values),
                                  "fog": newVariance(oldData,row,"fog",False,values),
                                  "lowClouds": newVariance(oldData,row,"lowClouds",False,values),
                                  "mediumClouds": newVariance(oldData,row,"mediumClouds",False,values),
                                  "highClouds": newVariance(oldData,row,"highClouds",False,values),
                                  "dewpointTemperature": newVariance(oldData,row,"dewpointTemperature",False,values),
                                  "precipitation": newVariance(oldData,row,"precipitation",False,values)}
    values["$set"]["longtermvar"]={"temperature": newVariance(oldData,row,"temperature",True,values),
                                  "windDirection": newVariance(oldData,row,"windDirection",True,values),
                                  "windSpeed": newVariance(oldData,row,"windSpeed",True,values),
                                  "windGust": newVariance(oldData,row,"windGust",True,values),
                                  "humidity": newVariance(oldData,row,"humidity",True,values),
                                  "pressure": newVariance(oldData,row,"pressure",True,values),
                                  "cloudiness": newVariance(oldData,row,"cloudiness",True,values),
                                  "fog": newVariance(oldData,row,"fog",True,values),
                                  "lowClouds": newVariance(oldData,row,"lowClouds",True,values),
                                  "mediumClouds": newVariance(oldData,row,"mediumClouds",True,values),
                                  "highClouds": newVariance(oldData,row,"highClouds",True,values),
                                  "dewpointTemperature": newVariance(oldData,row,"dewpointTemperature",True,values),
                                  "precipitation": newVariance(oldData,row,"precipitation",True,values)}
  if firstUpdate:
    values["$set"]["mean"]=      {"temperature":  row["temperature"],
                                  "windDirection": row["windDirection"],
                                  "windSpeed": row["windSpeed"],
                                  "windGust": row["windGust"],
                                  "humidity": row["humidity"],
                                  "pressure": row["pressure"],
                                  "cloudiness": row["cloudiness"],
                                  "fog": row["fog"],
                                  "lowClouds": row["lowClouds"],
                                  "mediumClouds": row["mediumClouds"],
                                  "highClouds": row["highClouds"],
                                  "dewpointTemperature": row["dewpointTemperature"],
                                  "precipitation": row["precipitation"]}
    values["$set"]["var"]=       {"temperature": 0,
                                  "windDirection": 0,
                                  "windSpeed": 0,
                                  "windGust": 0,
                                  "humidity": 0,
                                  "pressure": 0,
                                  "cloudiness": 0,
                                  "fog": 0,
                                  "lowClouds": 0,
                                  "mediumClouds": 0,
                                  "highClouds": 0,
                                  "dewpointTemperature": 0,
                                  "precipitation": 0}
    values["$set"]["longtermvar"]={"temperature": 0,
                                  "windDirection": 0,
                                  "windSpeed": 0,
                                  "windGust": 0,
                                  "humidity": 0,
                                  "pressure": 0,
                                  "cloudiness": 0,
                                  "fog": 0,
                                  "lowClouds": 0,
                                  "mediumClouds": 0,
                                  "highClouds": 0,
                                  "dewpointTemperature": 0,
                                  "precipitation": 0}
  values["$set"]["kjipestScore"]= kjiphet(values["$set"])
  collection.update_one(query, values, upsert=True) 

# Update all locations in database with new weather data.
def update_all_locations(df, collection):
  for _, row in df.iterrows():
    update_location(row, collection)
  # Create sorted index so calling sort on collection is quick.
  collection.create_index( [( "kjipestScore", -1 )] )

def recalc_kjiphet():
  print("Updating Kjiphet.")
  collection = connect_to_db()
  data = collection.find()
  for x in data:
    values = {"$set": {"kjipestScore": kjiphet(x)}}
    query = { "location": x["location"]}
    collection.update_one(query, values, upsert=True) 
  collection.create_index( [( "kjipestScore", -1 )] )
  print("All kjipestScore's updated.")

def test_db_update():
  print("Test of updating location")
  d = {"location": "Kristiansand",
    "temperature": [2],
    "windDirection": [2],
    "windSpeed": [2],
    "windGust": [2],
    "humidity": [2],
    "pressure": [2],
    "cloudiness": [2],
    "fog": [2],
    "lowClouds": [2],
    "mediumClouds": [2],
    "highClouds": [2],
    "dewpointTemperature": [2],
    "precipitation": [2],
    "lat": [58.16],
    "lon": [8.01],
    "prec_type": [1]}
  df = pd.DataFrame(d)
  # print(xx)
  collection = connect_to_db()
  update_all_locations(df,collection)
  query = { "location": "Kristiansand"}
  updatedData = collection.find(query)
  print(updatedData)
  for x in updatedData:
    print(x)

def plotCalcTempKjiphet():
  a = range(-35, 45)
  b = []
  for temp in a:
    b.append(calcTempKjiphet(temp))
  plt.plot(a,b)
  plt.show()
  input("Press key to stop")

# test_db_update()
recalc_kjiphet()
