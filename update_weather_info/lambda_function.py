import datetime as dt
import os
import json


import numpy as np
import pandas as pd
import pytz
from stravaclient import DynamoDBCache, StravaClient, OAuthHandler
from stravaclient.models.activity import UpdatableActivity
from tzwhere import tzwhere
from weatherapi.endpoint_methods import get_weather_history
from weatherapi.web_api.interface import APINotCalledException

from reporting import construct_weather_summary_string, generate_strava_activity_report
from hill_classification import get_report_summit_classifications
from hill_location import filter_visited_summits
from summit_report import generate_visited_summit_report


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    print("From SNS: ")
    print(message)

    token_cache = create_token_cache_from_env()
    strava_client = create_strava_client_from_env(token_cache)
    weather_api_key = os.environ.get('weather_api_key')

    # Parse athlete ID and activity ID
    athlete_id = message.get('athlete_id')
    activity_id = message.get('activity_id')
    print(f'Processing weather data for athlete {athlete_id}, activity {activity_id}')

    # Request activity information
    print(f'Requesting details for activity {activity_id}...')
    activity_info = strava_client.get_activity(athlete_id=athlete_id, activity_id=activity_id)

    # Load lat,lng coordinates
    start_lat = activity_info['start_latlng'][0]
    start_lng = activity_info['start_latlng'][1]
    activity_timezone = get_timezone_at_location(start_lat, start_lng)
    start_time = pd.to_datetime(activity_info['start_date']).to_pydatetime()
    start_time_local = convert_utc_to_timezone_at_location(start_time, activity_timezone)
    start_time_local = start_time_local.replace(tzinfo=None)
    duration = dt.timedelta(seconds=activity_info['elapsed_time'])
    end_time_local = start_time_local + duration

    print(f'Activity start coordinates: ({start_lat}, {start_lng})')
    print(f'Activity timezone: {activity_timezone}')
    print(f'Activity start time (UTC): {start_time}')
    print(f'Start time local: {start_time_local}')
    print(f'End time local: {end_time_local}')

    print(f'Retrieving weather data for {start_time_local}')
    try:
        weather_df = get_weather_history(api_key=weather_api_key,
                                         latitude=start_lat,
                                         longitude=start_lng,
                                         start_time=start_time_local,
                                         end_time=end_time_local)
    except APINotCalledException as e:
        print('Unable to call weather API')
        print(e)
        weather_df = None

    if weather_df is not None:
        weather_summary_message = construct_weather_summary_string(weather_df, start_time_local, end_time_local)
    else:
        weather_summary_message = None

    print('Generated summary message:')
    print(weather_summary_message)

    print(f'Requesting route stream data for activity {activity_id}')
    try:
        route_data = get_activity_stream_df(activity_id, athlete_id, strava_client)
        hills_database = pd.read_pickle('database.pkl')
        summits_to_report = filter_visited_summits(hills_database, route_data)
        reported_classifications = get_report_summit_classifications(summits_to_report)
        visited_summits_report = generate_visited_summit_report(reported_classifications, summits_to_report)
    except Exception as e:
        print('Unable to generate visited summit report:')
        print(e)
        visited_summits_report = None

    print('Generated summit report:')
    print(visited_summits_report)

    strava_report = generate_strava_activity_report(weather_report=weather_summary_message,
                                                    summit_report=visited_summits_report)

    # Request update to strava activity
    if strava_report is not None:
        add_report_to_activity_description(activity_id, activity_info, athlete_id, strava_client, strava_report)
    else:
        print('No data to report. Exiting...')

    print('Executed successfully')
    return {'statusCode': 200}


def add_report_to_activity_description(activity_id, activity_info, athlete_id, strava_client, strava_report):
    print('Editing activity with report: ')
    print(strava_report)
    new_activity = UpdatableActivity.from_activity(activity_info)
    print(new_activity.hide_from_home)
    new_activity.description = strava_report
    new_activity.hide_from_home = False
    print(new_activity.to_json())
    update = strava_client.update_activity(athlete_id=athlete_id,
                                           activity_id=activity_id,
                                           updatable_activity=new_activity)
    print(update)


def get_activity_stream_df(activity_id, athlete_id, strava_client):
    required_stream_columns = ['latlng', 'time', 'altitude']
    route_stream_json = strava_client.get_activity_stream_set(athlete_id=athlete_id,
                                                              activity_id=activity_id,
                                                              streams=required_stream_columns)
    for c in required_stream_columns:
        if c not in route_stream_json.keys():
            raise KeyError(f'Column {c} not available in datastream')
    route_data = parse_streams_dataframe(route_stream_json)
    return route_data


def create_strava_client_from_env(token_cache):
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    strava_authorisation = OAuthHandler(client_id=client_id,
                                        client_secret=client_secret,
                                        token_cache=token_cache)
    strava_client = StravaClient(strava_authorisation)
    return strava_client


def create_token_cache_from_env():
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    region_name = os.environ.get('region_name')
    table_name = os.environ.get('table_name')
    print('Connecting to authentication token database...')
    token_cache = DynamoDBCache(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name,
                                table_name=table_name)
    return token_cache


def get_timezone_at_location(latitude, longutude):
    timezone_locator = tzwhere.tzwhere()
    timezone_at_location = timezone_locator.tzNameAt(latitude=latitude, longitude=longutude)  # Seville coordinates
    return pytz.timezone(timezone_at_location)


def convert_utc_to_timezone_at_location(timestamp_utc, target_timezone):
    return timestamp_utc.astimezone(target_timezone)


def parse_streams_dataframe(streams_json):
    lat = np.array(streams_json['latlng']['data'])[:, 0]
    lng = np.array(streams_json['latlng']['data'])[:, 1]
    columns = streams_json.keys()
    df = pd.DataFrame()
    for col in columns:
        df[col] = streams_json[col]['data']
    df['lat'] = lat
    df['lng'] = lng
    return df


if __name__ == '__main__':
    result = lambda_handler('a', 'b')
