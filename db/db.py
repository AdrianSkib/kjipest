import pymongo
import pandas as pd
import datetime
import numpy as np
import math

# Sets up connection to server and returns the collection containing weather data for all locations.
# @Todo: Add authentication (preddy easy)
def connect_to_db():
  kjipestDBClient = pymongo.MongoClient("mongodb://localhost:27017/")
  kjipestDB = kjipestDBClient["KjipestDB"]
  collection = kjipestDB["Locations"]
  return collection

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

# Calculates the kjiphet of a location. Should use both current and historic weather data.
# @todo: Make this not be a constant.
def calc_kjiphet():
  return 4

# @todo: Tune! Also, add mean variance to db and use deviation of variance from this mean 
# variance instead of just variance
def calc_kjiphet_with_history(oldDataDF,newData):
  kjiphet = 0
  for oldData in oldDataDF:
    kjiphet += 0.001*sigmoid(float(oldData["temperature"]).var())
    # kjiphet += 0.001*sigmoid(float(oldData["windSpeed"]).var())
    # kjiphet += 0.001*sigmoid(float(oldData["precipitation"]).var())
    # kjiphet += 0.001*sigmoid(float(oldData["fog"]).var())
    # kjiphet += 0.001*sigmoid(float(oldData["lowClouds"]).var())
    # kjiphet += 0.001*sigmoid(float(oldData["mediumClouds"]).var())
    # kjiphet += 0.001*sigmoid(float(oldData["highClouds"]).var())
  return 100*sigmoid(kjiphet + calc_kjiphet_without_history(newData))

# @todo: Tune!
def calc_kjiphet_without_history(newData):
  kjiphet = 0
  kjiphet += 1*sigmoid(0.01*abs(25 - float(newData["temperature"])))
  # kjiphet += 10*sigmoid(float(newData["windSpeed"]))
  kjiphet += 1*sigmoid(0.01*float(newData["precipitation"]))
  # kjiphet += 1*sigmoid(float(newData["fog"]))
  # kjiphet += 1*sigmoid(float(newData["lowClouds"]))
  # kjiphet += 1*sigmoid(float(newData["mediumClouds"]))
  # kjiphet += 1*sigmoid(float(newData["highClouds"]))
  # Dunno about this man, must think about what the fuck dewpointTemp actually is.
  # kjiphet += 0.1*sigmoid(abs(float(newData["dewpointTemperature"])-float(newData["temperature"]))) 
  return 100*sigmoid(kjiphet)

# Inserts data from one location into database for the first time.
def update_location_first_time(row, collection):
  query = { "location": row["location"]}
  currentDate = datetime.date.today()
  values = { "$set": {"temperature":  [row["temperature"],0,0,0,0,0,0],
                        "windDirection": [row["windDirection"],0,0,0,0,0,0],
                        "windSpeed": [row["windSpeed"],0,0,0,0,0,0],
                        "windGust": [row["windGust"],0,0,0,0,0,0],
                        "humidity": [row["humidity"],0,0,0,0,0,0],
                        "pressure": [row["pressure"],0,0,0,0,0,0],
                        "cloudiness": [row["cloudiness"],0,0,0,0,0,0],
                        "fog": [row["fog"],0,0,0,0,0,0],
                        "lowClouds": [row["lowClouds"],0,0,0,0,0,0],
                        "mediumClouds": [row["mediumClouds"],0,0,0,0,0,0],
                        "highClouds": [row["highClouds"],0,0,0,0,0,0],
                        "dewpointTemperature": [row["dewpointTemperature"],0,0,0,0,0,0],
                        "precipitation": [row["precipitation"],0,0,0,0,0,0],
                        "latestUpdateDate": currentDate.strftime("%Y-%m-%d"),
                        "kjipestScore": 5}
                        }
                      
  collection.update_one(query, values, upsert=True)              

# Inserts data from one location into database.
def update_location(row, collection):
  # Get old data
  query = { "location": row["location"]}
  oldData = collection.find(query)
  # Get current date for comparison
  currentDate = datetime.date.today()
  # Check if data already has been updated today. If not then push new data and calc new score.
  updateBool = True
  popBool = False
  hadOldData = False
  kjiphet = 0
  for x in oldData:
    # print(x)
    if "latestUpdateTime" in x:
      latestUpdateDate = datetime.datetime.strptime(x["latestUpdateDate"], "%Y-%m-%d").date()
      # latestUpdateDate = datetime.datetime.strptime("2020-04-09", "%Y-%m-%d").date()
      # print(latestUpdateDate)
      if currentDate <= latestUpdateDate:
        updateBool = False
    if "temperature" in x and len(x["temperature"]) >= 7:
      popBool = True
    # Calc kjiphet
    hadOldData = True
    kjiphet = calc_kjiphet_with_history(oldData,row)
  updateBool = True
  if not hadOldData:
    kjiphet = calc_kjiphet_without_history(row)
  if updateBool:
    # Add newest data to end of arrays.
    values = { "$push": {"temperature":  row["temperature"],
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
                        }
    collection.update_one(query, values, upsert=True)      
    # Update kjiphet and latestUpdateDate
    values = {"$set": {"latestUpdateDate": currentDate.strftime("%Y-%m-%d"),
                        "kjipestScore": kjiphet}}
    collection.update_one(query, values, upsert=True)   
    if popBool:                      
      # Remove first element of vector
      values = { "$pop": {"temperature": -1,
                          "windDirection": -1,
                          "windSpeed": -1,
                          "windGust": -1,
                          "humidity": -1,
                          "pressure": -1,
                          "cloudiness": -1,
                          "fog": -1,
                          "lowClouds": -1,
                          "mediumClouds": -1,
                          "highClouds": -1,
                          "dewpointTemperature": -1}
                }   
    collection.update_one(query, values, upsert=True)                

# Update all locations in database with new weather data.
def update_all_locations(df, collection):
  for index, row in df.iterrows():
    # If you need to change structure of db, do so in this function and uncomment.
    update_location(row, collection)
    # update_location(row, collection)

def test_db_update():
  print("Test of updating Malvik")
  x = datetime.date.today()
  # print(x)
  xx = datetime.datetime.strptime("2020-04-08", "%Y-%m-%d").date()
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
    "precipitation": [2]}
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

# x = datetime.date.today()

# kjipestDBClient = pymongo.MongoClient("mongodb://localhost:27017/")
    # username='admin',
    # password='420SmokeIt',
    # authSource='the_database',
    # authMechanism='SCRAM-SHA-256')
# kjipestDB = kjipestDBClient["KjipestDB2"]
# kjipestDB.command("createUser", "admin", pwd="420SuckADick", roles=["root"])

# collection = kjipestDB["Locations"]
# print(kjipestDB.list_collection_names())

# mylist = [
#   { "name": "Lillesand", "temp": 69},
#   { "name": "Oslo", "temp": 420}
# ]
# insert_or_update("Grimstad", 40, tettstedCol)
# insert_or_update("Lillesand", 69, tettstedCol)
# insert_or_update("Oslo", 420, tettstedCol)

# insertResponse = tettstedCol.insert_many(mylist)
# print(insertResponse.inserted_ids)

# myquery = { "name": "Grimstad" }
# newvalues = { "$set": { "temp": 50 } }
# tettstedCol.update_one(myquery, newvalues, upsert=True)
# myquery = { "name": "Grimstad" }
# mydoc = tettstedCol.find(myquery)

# for x in mydoc:
#   print(x)

# mydoc = tettstedCol.find(myquery)

# for x in mydoc:
#   print(x)
###
# myquery = { "temp": { "$gt": 30 } }

# mydoc = tettstedCol.find(myquery)

# for x in mydoc:
#   print(x)

# tettstedCol.delete_many(myquery)


