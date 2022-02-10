import datetime as dt
import os
import json

import pandas as pd
import pytz
from stravaclient import DynamoDBCache, StravaClient, OAuthHandler
from stravaclient.models.activity import UpdatableActivity
from tzwhere import tzwhere
from weatherapi.endpoint_methods import get_weather_history


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    print("From SNS: ")
    print(message)

    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    region_name = os.environ.get('region_name')
    table_name = os.environ.get('table_name')

    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')

    weather_api_key = os.environ.get('weather_api_key')

    # Parse athlete ID and activity ID
    athlete_id = message.get('athlete_id')
    activity_id = message.get('activity_id')
    print(f'Processing weather data for athlete {athlete_id}, activity {activity_id}')

    # Retrieve authentication tokens from dynamodb
    print('Connecting to authentication token database...')
    token_cache = DynamoDBCache(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name,
                                table_name=table_name)

    strava_authorisation = OAuthHandler(client_id=client_id,
                                        client_secret=client_secret,
                                        token_cache=token_cache)

    strava_client = StravaClient(strava_authorisation)

    # Request activity information
    print(f'Requesting details for activity {activity_id}...')
    activity_info = strava_client.get_activity(athlete_id=athlete_id, activity_id=activity_id)

    # Load lat,lng coordinates
    start_lat = activity_info['start_latitude']
    start_lng = activity_info['start_longitude']
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
    weather_df = get_weather_history(api_key=weather_api_key,
                                     latitude=start_lat,
                                     longitude=start_lng,
                                     start_time=start_time_local,
                                     end_time=end_time_local)
    print(weather_df)

    # Construct weather summary message
    weather_summary_message = construct_weather_summary_string(weather_df, start_time_local, end_time_local)
    print('Generated summary message:')
    print(weather_summary_message)

    # Generate visited summit report

    # Request update to strava activity
    print('Editing activity...')
    new_activity = UpdatableActivity.from_activity(activity_info)
    new_activity.description = weather_summary_message
    strava_client.update_activity(athlete_id=athlete_id,
                                  activity_id=activity_id,
                                  updatable_activity=new_activity)

    # Return
    print('Executed successfully')
    return {'statusCode': 200}


def construct_weather_summary_string(df, start_time, end_time):
    start = pd.to_datetime(start_time).floor('1H')
    end = pd.to_datetime(end_time).ceil('1H')
    data = df.loc[(df.index >= start) & (df.index <= end)]
    degree_symbol = u'\N{DEGREE SIGN}'

    condition = data['condition'].mode().iloc[0]['text']
    temperature = data['temp_c'].mean()
    feels_like = data['feelslike_c'].min()
    windspeed = data['wind_mph'].mean()
    gust = data['gust_mph'].max()

    summary = (f"Condition: {condition}\n"
               f"Temperature: {temperature:.1f} {degree_symbol}C (feels like {feels_like:.1f} {degree_symbol}C)\n"
               f"Wind (mph): {windspeed:.1f}, gusting {gust:.1f}")

    return summary


def get_timezone_at_location(latitude, longutude):
    timezone_locator = tzwhere.tzwhere()
    timezone_at_location = timezone_locator.tzNameAt(latitude=latitude, longitude=longutude)  # Seville coordinates
    return pytz.timezone(timezone_at_location)


def convert_utc_to_timezone_at_location(timestamp_utc, target_timezone):
    return timestamp_utc.astimezone(target_timezone)
