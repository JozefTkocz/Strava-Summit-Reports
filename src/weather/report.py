import logging
from typing import Dict, Tuple
import pandas as pd
import datetime as dt
import pytz
from tzwhere import tzwhere

from weatherapi import get_weather_history


def generate_weather_report_for_activity(strava_activity: Dict, api_key: str) -> str:
    start_time_local, end_time_local = get_start_end_time_local(strava_activity)
    weather_data = download_weather_data_for_activity(strava_activity=strava_activity, api_key=api_key)
    return generate_weather_report_from_weather_data(weather_data, start_time=start_time_local, end_time=end_time_local)


def generate_weather_report_from_weather_data(df: pd.DataFrame, start_time: dt.datetime, end_time: dt.datetime) -> str:
    start = pd.to_datetime(start_time).floor('1H')
    end = pd.to_datetime(end_time).ceil('1H')
    data = df.loc[(df.index >= start) & (df.index <= end)]
    degree_symbol = u'\N{DEGREE SIGN}'
    condition = data['condition'].mode().iloc[0]['text']
    temperature = data['temp_c'].mean()
    feels_like = data['feelslike_c'].min()
    windspeed = data['wind_mph'].mean()
    gust = data['gust_mph'].max()

    summary = (f"Weather: {condition}\n"
               f"Temperature: {temperature:.1f} {degree_symbol}C (feels like {feels_like:.1f} {degree_symbol}C)\n"
               f"Wind (mph): {windspeed:.1f}, gusting {gust:.1f}")

    return summary


def download_weather_data_for_activity(strava_activity: Dict, api_key: str):
    start_lat = strava_activity['start_latlng'][0]
    start_lng = strava_activity['start_latlng'][1]
    start_time_local, end_time_local = get_start_end_time_local(strava_activity)

    try:
        weather_df = get_weather_history(api_key=api_key,
                                         latitude=start_lat,
                                         longitude=start_lng,
                                         start_time=start_time_local,
                                         end_time=end_time_local)
        logging.info(f'Retrieving weather data for {start_time_local}')
    except:
        logging.info('Unable to retrieve data from WeatherAPI')
        weather_df = None

    return weather_df


def get_start_end_time_local(strava_activity: Dict) -> Tuple[dt.datetime, dt.datetime]:
    start_lat = strava_activity['start_latlng'][0]
    start_lng = strava_activity['start_latlng'][1]
    activity_timezone = get_timezone_at_location(start_lat, start_lng)
    start_time = pd.to_datetime(strava_activity['start_date']).to_pydatetime()
    start_time_local = convert_utc_to_timezone_at_location(start_time, activity_timezone)
    start_time_local = start_time_local.replace(tzinfo=None)
    duration = dt.timedelta(seconds=strava_activity['elapsed_time'])
    end_time_local = start_time_local + duration
    return start_time_local, end_time_local


def get_timezone_at_location(latitude: float, longitude: float) -> dt.tzinfo:
    timezone_locator = tzwhere.tzwhere(forceTZ=True)
    timezone_at_location = timezone_locator.tzNameAt(latitude=latitude, longitude=longitude, forceTZ=True)
    return pytz.timezone(timezone_at_location)


def convert_utc_to_timezone_at_location(timestamp_utc: dt.datetime, target_timezone: dt.tzinfo) -> dt.datetime:
    return timestamp_utc.astimezone(target_timezone)
