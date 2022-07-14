import json
import os
import logging
from typing import Dict, Union

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # Respond immediately to the webhook subscription challenge if this endpoint is being registered with the Strava
    # webhook API for the first time
    challenge = parse_challenge_from_query_string(event)

    if challenge is not None:
        logging.info('Responding to Strava subscription challenge')
        return {'statusCode': 200,
                'body': json.dumps({'hub.challenge': challenge})}

    # Otherwise parse the incoming webhook event and publish to AWS notification service for later processing
    event_body = parse_json_body(event)
    if not is_newly_created_activity(event_body):
        logging.info('Not a new activity, exiting early...')
        return {'statusCode': 200}

    athlete_id = event_body.get('owner_id')
    activity_id = event_body.get('object_id')
    topic = create_sns_topic_from_env()
    message = {'athlete_id': athlete_id,
               'activity_id': activity_id}

    logging.info(f'Creating event for athlete {athlete_id}, activity {activity_id}')
    try:
        response = topic.publish(Message=json.dumps(message))
        message_id = response['MessageId']
        logging.info(f'Successfully published message with ID: {message_id}')
    except ClientError:
        logging.info('Unable to publish message.')

    return {'statusCode': 200}


def create_sns_topic_from_env():
    region_name = os.environ.get('region_name')
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    sns_resource = os.environ.get('sns_resource')

    sns_client = boto3.resource('sns',
                                region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
    topic = sns_client.Topic(sns_resource)
    return topic


def is_newly_created_activity(body: Dict) -> bool:
    object_type = body.get('object_type')
    aspect_type = body.get('aspect_type')
    # Only publish events that are new athlete activities
    is_activity = object_type == 'activity'
    is_newly_created = aspect_type == 'create'
    return is_activity and is_newly_created


def parse_json_body(event: Dict) -> Dict:
    body = event.get('body')
    body = json.loads(body)
    return body


def parse_challenge_from_query_string(event: Dict) -> Union[str, None]:
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is not None:
        challenge = queryStringParameters.get('hub.challenge')
    else:
        challenge = None
    return challenge
