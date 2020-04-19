import pymongo
import pandas as pd
import datetime
import numpy as np
import math
import bson
from bson.raw_bson import RawBSONDocument

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
    return oldVar + oldMean*oldMean - newMean*newMean + (newMeasurement*newMeasurement - oldVar - oldMean*oldMean)/(shortTermWindowSize+1)
  else:
    return oldVar + oldMean*oldMean - newMean*newMean + (newMeasurement*newMeasurement - oldVar - oldMean*oldMean)/(longTermWindowSize+1)

def newVariance(oldData,row,field,shortTerm,values):
  return movingVar(oldData["var"][field],oldData["mean"][field],values["$set"]["mean"][field],row[field],shortTerm)

# Calculates the kjiphet of a location. 
def kjiphet(data):
  return 100*sigmoid(0.1*abs(25-float(data["values"]["temperature"])))

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

# test_db_update()

