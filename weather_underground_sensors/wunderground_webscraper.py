import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as BS
import requests
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

if not os.path.exists(BASE_DIR / 'weather_underground_sensors' / 'data'):
    os.makedirs('data')


def scrape_wunderground(station, date):
    """Given a PWS station ID and date, scrape that day's data from Weather
    Underground and return it as a dataframe.

    Parameters
    ----------
        station : str
            The personal weather station ID
        date : str
            The date for which to acquire data, formatted as 'YYYY-MM-DD'

    Returns
    -------
        df : dataframe or None
            A dataframe of weather observations, with index as pd.DateTimeIndex
            and columns as the observed data
    """
    # Construct the URL
    url = f'https://www.wunderground.com/dashboard/pws/{station}/table/' \
          f'{date}/{date}/daily'

    # Make an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BS(response.text, "html.parser")

        container = soup.find('lib-history-table')

        # Check that lib-history-table is found
        if container is None:
            raise ValueError(
                f"could not find lib-history-table in html source for {url}")

        # Get the timestamps and data from two separate 'tbody' tags
        all_checks = container.find_all('tbody')
        time_check = all_checks[0]
        data_check = all_checks[1]

        # Iterate through 'tr' tags and get the timestamps
        hours = [i.get_text() for i in time_check.find_all('tr')]

        # For data, locate both value and no-value ("--") classes
        classes = ['wu-value wu-value-to', 'wu-unit-no-value ng-star-inserted']

        # Iterate through span tags and get data
        data = [i.get_text() for i in data_check.find_all(
            'span', class_=classes)]

        columns = ['Temperature', 'Dew Point', 'Humidity', 'Wind Speed',
                   'Wind Gust', 'Pressure', 'Precip. Rate', 'Precip. Accum.']

        # Convert NaN values (stings of '--') to np.nan
        data_nan = [np.nan if x == '--' else x for x in data]

        # Convert list of data to an array
        data_array = np.array(data_nan, dtype=float)
        data_array = data_array.reshape(-1, len(columns))

        # Prepend date to HH:MM strings
        timestamps = [f'{date} {t}' for t in hours]

        # Convert to dataframe
        df = pd.DataFrame(index=timestamps, data=data_array, columns=columns)
        df.index = pd.to_datetime(df.index)

        return df
    else:
        print(f"Failed to retrieve data for {station} on {date}. "
              f"Status code: {response.status_code}")
        return None


def scrape_multiattempt(station, date, attempts=4, wait_time=5.0):
    """Try to scrape data from Weather Underground. If there is an error on the
    first attempt, try again.

    Parameters
    ----------
        station : str
            The personal weather station ID
        date : str
            The date for which to acquire data, formatted as 'YYYY-MM-DD'
        attempts : int, default 4
            Maximum number of times to try accessing before failuer
        wait_time : float, default 5.0
            Amount of time to wait in between attempts

    Returns
    -------
        df : dataframe or None
            A dataframe of weather observations, with index as pd.DateTimeIndex
            and columns as the observed data
    """

    # Try to download data limited number of attempts
    for n in range(attempts):
        try:
            df = scrape_wunderground(station, date)
        except Exception as ex:
            print(ex)
            # if unsuccessful, pause and retry
            time.sleep(wait_time)
        else:
            # if successful, then break
            break
    # If all attempts failed, return empty df
    else:
        df = pd.DataFrame()

    return df


def main():
    # List of 50 station IDs
    station_ids = ['IDUBLI64']  # add remaining station IDs

    # Loop through each station ID and date range
    for station in station_ids:
        for date in pd.date_range('2023-11-05', '2023-11-05'):
            date_str = date.strftime('%Y-%m-%d')
            print(f'Scraping data for {station} on {date_str}')

            # Try to download data
            df = scrape_wunderground(station, date_str)

            # If successful, save to csv
            if df is not None:
                filename = f'data/{station}_{date_str}.csv'
                df.to_csv(filename)
                print(f'Successfully saved data to {filename}')
            else:
                print(f'Failed to scrape data for {station} on {date_str}')


if __name__ == '__main__':
    main()
