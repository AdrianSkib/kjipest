
import requests 
import xml.etree.ElementTree as ET 
  
import pandas as pd
import numpy as np
import json


import xmltodict




def get_forecast_xml(lat: float, lng: float):
    """
    Query the locationforecast endpoint to retrieve weather forecast for specified location
    
    
    return: reponse in xml binary data
    """
    
    # Define fixed endpoint
    endpoint = 'https://api.met.no/weatherapi/locationforecast/1.9/?'
    parameters = {
        'lat': lat,
        'lon': lng,
    }
    # Issue an HTTP GET request
    r = requests.get(endpoint, parameters)

    # Return xml data
    return r.content



def parse_weatherforecast(lat, lon):
    """
    Parse relevant info from json response, using only the most recent (0 indexed)
    forecast entry.
    
    return: dict of relevant data
    """
    
    # Dict of indices used to parse relevant values from response 
    forecast_index_dict = {
        'temperature': '@value',
        'windDirection': '@deg',
        'windSpeed': '@mps',
        'windGust': '@mps',
        'humidity': '@value',
        'pressure': '@value',
        'cloudiness': '@percent',
        'fog': '@percent',
        'lowClouds': '@percent',
        'mediumClouds': '@percent',
        'highClouds':'@percent',
        'dewpointTemperature': '@value'
    }

    
    
    # Retrieve data and parse to dict
    xml_data = get_forecast_xml(lat, lon)
    
    parsed_data = xmltodict.parse(xml_data)
    
    if 'weatherdata' in parsed_data.keys():
        dict_data = parsed_data['weatherdata']['product']['time']
    
        # Get time index
        timestamp = dict_data[0]['@from']

        # Get first index (now)
        nowcast = dict_data[0]['location']

        # Parse relevant data
        now_dict = {'timestamp': timestamp}
        for var, var_key in forecast_index_dict.items():

            # Check data is present
            if var in nowcast.keys():
                if var_key in nowcast[var].keys(): 
                    now_dict.update({var: nowcast[var][var_key]})

            else:
                now_dict.update({var: np.nan})


        return now_dict
    
    else:
        # Error response
        return 0



def get_current_weather(location_df, name_col = 'kommune'):
    """
    Queries current forecast on all locations in location_df, given by lat lon coordinates.
    
    
    return: df with relevant information
    """

    
    assert 'lat' in location_df.columns, f"required column lat not in location_df (Columns: {location_df.columns})"
    assert 'lon' in location_df.columns, f"required column lon not in location_df (Columns: {location_df.columns})"
    assert name_col in location_df.columns, f"required cloumn {name_col} in location_df (Columns: {location_df.columns})"
    
    row_list = []
    
    # Iterate over location_df to get coordinates
    for _, row in location_df.iterrows():
        
        # Get forecast
        forecast_row = parse_weatherforecast(row.lat, row.lon)
        
        # Check successful operation
        if forecast_row != 0:
            forecast_row.update({name_col: row[name_col]})
        
            # Append to list
            row_list.append(forecast_row)
        
    forecast_df = pd.DataFrame(row_list)
    
    return(forecast_df)