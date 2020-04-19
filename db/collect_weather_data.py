import pandas as pd
import numpy as np
import time
import os
import datareader, met_api
from db import *
import math

# Collects weather data and updates the database.
def update_database():
    # Connect to database
    collection = connect_to_db()

    # Read data
    locations_path = 'csv/locations.csv'
    locations_df = pd.read_csv(os.path.abspath(locations_path), index_col = 0, converters={'geometry.coordinates': lambda x: x.strip("[]").split(", ")})

    # Format locations df to desired format
    lats = [float(coord[1]) for coord in locations_df['geometry.coordinates'].values]
    lons = [float(coord[0]) for coord in locations_df['geometry.coordinates'].values]
    locations_df['lat'] = lats
    locations_df['lon'] = lons
    locations_df = locations_df.rename(columns = {'name': 'location'})
    

    # Get forecats
    # tic = time.clock()
    forecast_df = met_api.get_current_weather(locations_df, name_col = 'location')
    # toc = time.clock()
    # toc - tic
        
    # Update all locations in database 
    update_all_locations(forecast_df,collection)
    print("All locations updated with fresh weather data.")

def collection_loop():
    print("Starting collection loop")
    while True:
        print("Updating...")
        tic = time.clock()
        update_database()
        toc = time.clock()
        diff = (toc - tic)
        print("Used " + str(math.floor(diff)) + " seconds to update database.")
        waitTime = 60*15 - math.floor(diff)
        if waitTime > 0:
            print(str(math.floor(waitTime/6)/10) + " minutes until next update.")
            time.sleep(waitTime) # Makes sure the update is run every 15th minute

collection_loop()
