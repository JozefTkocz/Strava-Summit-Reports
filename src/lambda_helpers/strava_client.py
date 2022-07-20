import os
import logging
from typing import Dict

from stravaclient import OAuthHandler, DynamoDBCache, StravaClient
from stravaclient.models.activity import UpdatableActivity


def create_strava_client_from_env():
    client_id = int(os.environ.get('client_id'))
    client_secret = os.environ.get('client_secret')
    token_cache = create_token_cache_from_env()
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
    logging.info('Connecting to authentication token database...')
    token_cache = DynamoDBCache(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name,
                                table_name=table_name)
    return token_cache


def add_report_to_activity_description(activity_id: int, athlete_id: int, strava_client: StravaClient,
                                       strava_report: str, activity_info: Dict):
    new_activity = UpdatableActivity.from_activity(activity_info)
    new_activity.description = strava_report
    update = strava_client.update_activity(athlete_id=athlete_id,
                                           activity_id=activity_id,
                                           updatable_activity=new_activity)
