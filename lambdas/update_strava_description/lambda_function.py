import json
import logging
import os

from summits import report_visited_summits
from lambda_helpers import create_strava_client_from_env
from stravaclient.models.activity import UpdatableActivity


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logging.info("Event received from SNS:")
    logging.info(message)

    strava_client = create_strava_client_from_env()
    weather_api_key = os.environ.get('weather_api_key')

    # Parse athlete ID and activity ID
    athlete_id = message.get('athlete_id')
    activity_id = message.get('activity_id')
    activity_data = strava_client.get_activity(athlete_id=athlete_id, activity_id=activity_id)
    activity = UpdatableActivity.from_activity(activity_data)
    try:
        route_data = strava_client.get_activity_stream_set(athlete_id=athlete_id,
                                                           activity_id=activity_id,
                                                           streams=['latlng'],
                                                           as_df=True)
        summit_report = report_visited_summits(lat=route_data['lat'].values,
                                               lng=route_data['lng'].values,
                                               database_filepath='./database.pkl')
    except:
        logging.exception('Unable to generate visited summits report')
        summit_report = None

    logging.info('Generated summit report:')
    logging.info(summit_report)
    strava_report = summit_report

    # Request update to strava activity
    if strava_report is not None:
        activity.description = strava_report
        strava_client.update_activity(activity)
    else:
        logging.info('No data to report. Exiting...')

    return {'statusCode': 200}
