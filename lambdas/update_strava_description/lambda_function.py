import json
import logging
from stravaclient import StravaClient

from summits import report_visited_summits


def create_strava_client_from_env() -> StravaClient:
    return StravaClient()


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
    activity_info = strava_client.get_activity(athlete_id=athlete_id, activity_id=activity_id)
    try:
        route_data = strava_client.get_activity_stream_set(athlete_id=athlete_id,
                                                           activity_id=activity_id,
                                                           streams=,
                                                           as_df=True)
        summit_report = report_visited_summits(lat=route_data['lat'].values,
                                               lng=route_data['lng'].values,
                                               database_filepath='./database.pkl')
    except Exception as e:
        logging.exception('Unable to generate visited summits report')
        visited_summits_report = None

    print('Generated summit report:')
    print(summit_report)

    strava_report = summit_report

    # Request update to strava activity
    if strava_report is not None:
        add_report_to_activity_description(activity_id, activity_info, athlete_id, strava_client, strava_report)
    else:
        print('No data to report. Exiting...')

    print('Executed successfully')
    return {'statusCode': 200}
