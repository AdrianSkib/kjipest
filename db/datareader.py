from utm.conversion import to_latlon


import requests 
import xml.etree.ElementTree as ET 
  
import pandas as pd
import numpy as np
import json


import xmltodict


def read_geojson(path):
    """
    Reads geojson file downloaded from:
    https://kartkatalog.geonorge.no/metadata/administrative-enheter-kommuner-gjeldende/041f1e6e-bdbc-4091-b48f-8a5990f3cc5b
        Projection: EUREF89 UTM sone 33, 2d
    
    return: DataFrame with centroid of coordinate polygon in lat lon, and name of kommune.
    """
    
    
    # Read geojson file 
    kommune_df  = pd.read_json(path)

    # Get relevant data
    kommune_list = kommune_df.T['features']['administrative_enheter.kommune']
    
    row_list = []
    
    # Iterate over every kommune and parse coordinate info
    for element in kommune_list:
        
        name = element['properties']['navn'][0]['navn']
        
        # The coordinates define a polygon giving the borders.
        # We use the the centroid:
        x_coord = np.mean([coord[0] for coord in element['geometry']['coordinates'][0]])
        y_coord = np.mean([coord[1] for coord in element['geometry']['coordinates'][0]])
        
        # Convert to latlon
        # NOTE: Blind sampling give small discrepencies in lat lon coordinates and actual kommune center
        lat_lon = to_latlon(x_coord,y_coord, zone_number = 33, northern = True, strict = False)
        
        
        # Define row as dict
        row = {'kommune': name,
               'lat': lat_lon[0],
              'lon': lat_lon[1]
        }
        
        row_list.append(row)
    
    return(pd.DataFrame(row_list))