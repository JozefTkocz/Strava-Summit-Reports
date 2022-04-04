import os
import time

import numpy as np
import pandas as pd
from stravaclient import StravaClient, OAuthHandler, DynamoDBCache

from update_weather_info.hill_classification import get_report_summit_classifications
from update_weather_info.hill_location import get_candidate_summits_from_local_maxima, filter_visited_summits
from update_weather_info.lambda_function import parse_streams_dataframe
from update_weather_info.summit_report import generate_visited_summit_report


def parse_strava_activities_to_dataframe(activities_json):
    df = pd.DataFrame(dtype=object)
    for activity in activities_json:
        activity_id = int(activity['id'])
        name = activity['name']
        start_time = pd.to_datetime(activity['start_date'])
        elapsed_time = activity['elapsed_time']
        moving_time = activity['moving_time']
        end_time = start_time + pd.Timedelta(elapsed_time, unit='seconds')
        distance = activity['distance']
        elevation_gain = activity['total_elevation_gain']
        activity_type = activity['type']

        row = {
            'activity_id': activity_id,
            'name': name,
            'start_time': start_time,
            'elapsed_time_s': elapsed_time,
            'moving_time_s': moving_time,
            'end_time': end_time,
            'distance_m': distance,
            'elevation_gain_m': elevation_gain,
            'activity_type': activity_type

        }

        df = pd.concat([df, pd.DataFrame.from_records([row])], ignore_index=True)
        df['activity_id'] = df['activity_id'].astype(np.int64)

    return df.set_index('activity_id')


def main():
    USE_CACHED_ACTIVITIES = True
    athlete_id = 36371430
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    region_name = 'None'
    table_name = os.environ.get('table_name')

    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')

    weather_api_key = os.environ.get('weather_api_key')

    token_cache = DynamoDBCache(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name,
                                table_name=table_name)

    strava_authorisation = OAuthHandler(client_id=client_id,
                                        client_secret=client_secret,
                                        token_cache=token_cache)

    strava_client = StravaClient(strava_authorisation)

    if not USE_CACHED_ACTIVITIES:
        end_of_activities = False
        results_per_page = 30
        iteration = 1
        activities_dataframe = pd.DataFrame()
        while not end_of_activities:
            print(f'requesting_activities, iteration {iteration}')
            activities = strava_client.list_activities(athlete_id=athlete_id, page=iteration, per_page=30)
            iteration += 1
            if not len(activities) == results_per_page:
                end_of_activities = True

            page_df = parse_strava_activities_to_dataframe(activities)
            activities_dataframe = pd.concat([activities_dataframe, page_df])

        activities_dataframe.to_csv('./strava_activities.csv')
    else:
        activities_dataframe = pd.read_csv('./strava_activities.csv', index_col=0)

    print(activities_dataframe)

    hills_database = pd.read_pickle('database.pkl')

    for activity, data in activities_dataframe.iterrows():
        print(f'processing activity {activity}: {data["name"]}')
        try:
            required_stream_columns = ['latlng', 'time', 'altitude']
            route_stream_json = strava_client.get_activity_stream_set(athlete_id=athlete_id,
                                                                      activity_id=activity,
                                                                      streams=required_stream_columns)

            # If we've hit the rate limit, sleep for 15 minutes and try again
            if route_stream_json.get('messsage') == "Rate Limit Exceeded":
                time.sleep(15.5 * 60)
                route_stream_json = strava_client.get_activity_stream_set(athlete_id=athlete_id,
                                                                          activity_id=activity,
                                                                          streams=required_stream_columns)

            for c in required_stream_columns:
                if c not in route_stream_json.keys():
                    raise KeyError(f'Column {c} not available in datastream')

            route_data = parse_streams_dataframe(route_stream_json)
            summits = get_candidate_summits_from_local_maxima(route_data)
            summits_to_report = filter_visited_summits(hills_database, summits)
            reported_classifications = get_report_summit_classifications(summits_to_report)
            visited_summits_report = generate_visited_summit_report(reported_classifications, summits_to_report)

            summit_names = summits_to_report['Name'].unique()
            print(summit_names)
            print(visited_summits_report)

        except Exception as e:
            print('Unable to generate visited summit report:')
            print(e)
            visited_summits_report = None
            summit_names = None

        activities_dataframe.loc[activity, 'report'] = visited_summits_report
        activities_dataframe.loc[activity, 'Summits'] = str(summit_names)

    activities_dataframe.to_csv('strava_activities_reports.csv')


if __name__ == '__main__':
    main()
