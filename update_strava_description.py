import json
import logging
import os
from typing import List, Union

from summits import report_visited_summits
from lambda_helpers.strava_client import create_strava_client_from_env
from stravaclient.models.activity import UpdatableActivity
from weather.report import generate_weather_report_for_activity


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

    weather_report = get_weather_report(activity_data, weather_api_key)
    summit_report = get_summit_report(activity_id, athlete_id, strava_client)
    strava_report = create_strava_description([summit_report, weather_report])

    logging.info('Generated Strava Report')
    logging.info(strava_report)

    if strava_report is not None:
        activity.description = strava_report
        strava_client.update_activity(activity)
    else:
        logging.info('No data to report. Exiting...')

    return {'statusCode': 200}


def create_strava_description(reports: List[Union[str, None]]) -> Union[str, None]:
    final_report = None

    def append_reports(main_report: Union[str, None], sub_report: Union[str, None]) -> Union[str, None]:
        if main_report is None:
            return sub_report
        elif sub_report is None and main_report is not None:
            return main_report
        else:
            return main_report + '\n\n' + sub_report

    for report in reports:
        final_report = append_reports(final_report, report)

    return final_report


def get_summit_report(activity_id, athlete_id, strava_client):
    try:
        route_data = strava_client.get_activity_stream_set(athlete_id=athlete_id,
                                                           activity_id=activity_id,
                                                           streams=['latlng'],
                                                           as_df=True)
        return report_visited_summits(lat=route_data['lat'].values,
                                      lng=route_data['lng'].values,
                                      database_filepath='./database.pkl')
    except:
        logging.exception('Unable to generate visited summits report')
        return None


def get_weather_report(activity_data, weather_api_key):
    try:
        return generate_weather_report_for_activity(strava_activity=activity_data,
                                                    api_key=weather_api_key)
    except:
        logging.exception('Unable to generate weather report')
        return None


if __name__ == '__main__':
    print(create_strava_description(['Report A', 'Report B', 'Report C']))
