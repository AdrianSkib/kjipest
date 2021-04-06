import datetime
import logging
import sys
sys.path.append("..") # Adds higher directory to python modules path.
from collect_weather_data import update_database

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    update_database()
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
