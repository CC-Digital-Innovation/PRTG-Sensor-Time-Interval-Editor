import csv
import io
import logging
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime

import configparser
import requests
import pandas as pd
import pytz


# Module information.
__author__ = 'Anthony Farina'
__copyright__ = 'Copyright 2021, PRTG Sensor Time Interval Editor'
__credits__ = ['Anthony Farina']
__license__ = 'MIT'
__version__ = '1.0.1'
__maintainer__ = 'Anthony Farina'
__email__ = 'farinaanthony96@gmail.com'
__status__ = 'Released'


# General global variables.
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# Global variables from the config file for easy referencing.
CONFIG = configparser.ConfigParser()
CONFIG_PATH = '/../configs/PRTG-Sensor-Time-Interval-Editor-config.ini'
CONFIG.read(SCRIPT_PATH + CONFIG_PATH)
SERVER_URL = CONFIG['PRTGInfo']['server_url']
USERNAME = urllib.parse.quote_plus(CONFIG['PRTGInfo']['username'])
PASSWORD = urllib.parse.quote_plus(CONFIG['PRTGInfo']['password'])
PASSHASH = urllib.parse.quote_plus(CONFIG['PRTGInfo']['passhash'])
TIMEZONE = CONFIG['TimezoneInfo']['timezone']


# This function will go into the provided PRTG instance and edit the time
# intervals for sensors by name. PRTG may need to be restarted once the script
# stops. It will log which sensors were edited and when in a log file.
def prtg_sensor_time_interval_editor() -> None:
    # Make a logger that logs what's happening in a log file and the console.
    now_log = datetime.utcnow().replace(tzinfo=pytz.UTC).astimezone(
        pytz.timezone(TIMEZONE))
    logging.basicConfig(filename=SCRIPT_PATH + '/../logs/time_interval_log-' +
                        now_log.strftime('%Y-%m-%d_%I-%M-%S-%p-%Z') + '.log',
                        level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%m-%d-%Y %I:%M:%S %p %Z')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Prepare the PRTG API call URL that will get all the sensors.
    sensor_url = SERVER_URL + \
                 '/api/table.xml?content=sensors' \
                 '&output=csvtable&columns=probe,group,device,name,objid,' \
                 'interval&count=50000&username=' + USERNAME
    sensor_url = add_auth(sensor_url)

    # Get the sensor information from PRTG.
    logging.info('Retrieving all sensors from PRTG...')
    sensor_resp = requests.get(url=sensor_url)
    logging.info('All sensors retrieved from PRTG!')

    # Make a clean dataframe object from the sensor information received.
    logging.info('Formatting response from PRTG...')
    sensor_resp_csv_strio = io.StringIO(sensor_resp.text)
    sensor_resp_csv_df = pd.read_csv(sensor_resp_csv_strio)
    sensor_resp_csv_df = remove_raw(sensor_resp_csv_df)

    # Turn the CSV response dataframe and interpret it as a dictionary.
    sensor_csv_str = sensor_resp_csv_df.to_csv(sep=',', index=False,
                                               encoding='utf-8')
    sensor_csv_strio = io.StringIO(sensor_csv_str)
    sensor_dict = csv.DictReader(sensor_csv_strio)
    logging.info('Response from PRTG has been formatted!')

    # Count the number of successful and unsuccessful edits along with the
    # script stop reason and connection reuse object.
    edits = 0
    errors = 0
    reason_msg = 'Sensors edited from PRTG.'
    edit_sess = requests.Session()

    # Iterate through all PRTG sensors and edit specified sensors by name.
    for sensor in sensor_dict:
        # Check if this sensor's time interval needs to be edited.
        if sensor['Object'] == 'Example Sensor Name' or \
           sensor['Interval'] == '1 h' or sensor['Interval'] == '30 m':
            # Log and attempt to edit the sensor's time interval from PRTG.
            logging.info('Editing time interval of sensor "' + sensor['Object']
                         + '" for device "' + sensor['Device'] + '" [ID: '
                         + sensor['ID'] + ']...')

            # Run PowerShell script to switch the interval inheritance off.
            powershell_script = subprocess.Popen(
                ['powershell.exe', os.path.dirname(os.path.realpath(__file__))
                 + '/Switch-Inheritance-Off.ps1 ' + sensor['ID']],
                stdout=sys.stdout)
            powershell_script.communicate()

            # Prepare edit URL. 'value' should be edited to the new desired
            # time interval for the sensor.
            value = 3600
            edit_url = SERVER_URL + \
                       '/api/setobjectproperty.htm?id=' + sensor['ID'] + \
                       '&name=interval&value=' + str(value) + \
                       '&username=' + USERNAME
            edit_url = add_auth(edit_url)

            # OPTIONAL: Sleep before the next request to ease stress on PRTG
            # server. This depends how responsive the given PRTG instance is.
            # time.sleep(5)

            # Set up the logic needed to retry failed connections up to 3
            # times. If the connection can't be made, end the program.
            edit_resp = None
            count = 0
            max_retries = 3

            # Try and retry until a successful connection is made,
            # otherwise, end the program.
            while count < max_retries:
                try:
                    edit_resp = edit_sess.get(url=edit_url)
                    break
                except requests.exceptions.RequestException as e:
                    count += 1
                    if count < max_retries:
                        logging.warning('The connection to ' + edit_url +
                                        ' failed. Retrying the connection '
                                        'in 5 minutes...')
                        time.sleep(300)
                    else:
                        logging.error('Error: Maximum connection retries '
                                      'exceeded. Ending the script.')
                        log_results('Connection timed out.', edits, errors)
                        SystemExit(e)

            # Check if the time interval edit was successful.
            if edit_resp.status_code != 200:
                logging.error('Error editing the time interval of sensor -'
                              + '- [Probe: ' + sensor['Probe']
                              + '] [Group: ' + sensor['Group']
                              + '] [Device: ' + sensor['Device']
                              + '] [Sensor Name: ' + sensor['Object']
                              + '] [Sensor ID: ' + sensor['ID'] + '] -- ')
                logging.error('Caused by: ' + str(edit_resp.status_code))
                logging.error(edit_resp.reason)
                errors += 1
            # The time interval edit was successful.
            else:
                logging.info('Sensor -- [Probe: ' + sensor[
                    'Probe'] + '] [Group: ' + sensor['Group']
                             + '] [Device: ' + sensor['Device']
                             + '] [Sensor Name: ' + sensor['Object']
                             + '] [Sensor ID: ' + sensor['ID']
                             + '] -- time interval was successfully edited '
                             + 'from PRTG!')
                edits += 1

    # Close the connection to the PRTG server.
    edit_sess.close()

    # Log the results and end the script.
    log_results(reason_msg, edits, errors)


# Every time table information is called from the PRTG API, the response has
# 'readable' columns and 'raw' columns. Their are subtle differences,
# but the raw columns are not needed. This function removes all the 'raw'
# columns from a dataframe object of the PRTG API response and returns a
# dataframe object with only the non-raw columns.
def remove_raw(raw_df: pd.DataFrame) -> pd.DataFrame:
    # Prepare a list of desired column names.
    col_labels = list()

    # Iterate through the column labels to remove column labels ending with
    # '(RAW)'.
    for col in raw_df.columns:
        # Add only desired column labels to the list.
        if not bool(re.search('\\(RAW\\)$', col)):
            col_labels.append(col)

    # Return the dataframe object that only has desired columns.
    return_df = raw_df[col_labels]
    return return_df


# This function will append the PRTG authentication to the end of the given
# PRTG API call URL. It will append either the password or passhash,
# whichever was provided in the config file. Passhash has priority if both
# fields are filled in.
def add_auth(url: str) -> str:
    # Check if the password or passhash will be used to authenticate the
    # access to the PRTG instance.
    if PASSHASH == '':
        url = url + '&password=' + PASSWORD
    else:
        url = url + '&passhash=' + PASSHASH

    return url


# This function will print the results of the script's successes and/or
# failures to the end of the log file.
def log_results(reason: str, edits: int, errors: int) -> None:
    # Log the results to the log file.
    logging.info('')
    logging.info('===========================================================')
    logging.info('')
    logging.info('Time interval edit job completed. ' + reason)
    logging.info('Total time interval edits: ' + str(edits))
    logging.info('Total time interval edit errors: ' + str(errors))


# The main method that runs the script. There are no input arguments.
if __name__ == '__main__':
    # Check to make sure the logs folder exists. If not, create it.
    if not os.path.isdir(SCRIPT_PATH + '/../logs'):
        os.mkdir(SCRIPT_PATH + '/../logs')

    # Run the script.
    prtg_sensor_time_interval_editor()
