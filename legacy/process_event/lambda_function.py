import json
import os

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # Respond immediately to the webhook subscription challenge if this endpoint is being registered with the Strava
    # webhook API for the first time
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is not None:
        challenge = queryStringParameters.get('hub.challenge')
    else:
        challenge = None

    if challenge is not None:
        print('Responding to Strava subscription challenge')
        return {
            'statusCode': 200,
            'body': json.dumps({'hub.challenge': challenge})
        }

    region_name = os.environ.get('region_name')
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    sns_resource = os.environ.get('sns_resource')

    # Otherwise parse the incoming webhook event and publish to AWS notification service for later processing
    body = event.get('body')
    print('body')
    body = json.loads(body)
    object_type = body.get('object_type')
    aspect_type = body.get('aspect_type')

    # Only publish events that are new athlete activities
    is_activity = object_type == 'activity'
    is_newly_created = aspect_type == 'create'

    print(f'newly_created: {is_newly_created}')
    print(f'is_activity: {is_activity}')

    if not (is_activity and is_newly_created):
        print('Not a new activity, exiting early...')
        return {
            'statusCode': 200,
            'body': json.dumps({'is_activity': is_activity,
                                'is_newly_created': is_newly_created})
        }

    athlete_id = body.get('owner_id')
    activity_id = body.get('object_id')

    print(f'Creating event for athlete {athlete_id}, activity {activity_id}')

    sns_client = boto3.resource('sns',
                                region_name=region_name,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key)
    topic = sns_client.Topic(sns_resource)

    message = {'athlete_id': athlete_id,
               'activity_id': activity_id}

    try:
        response = topic.publish(Message=json.dumps(message))
        message_id = response['MessageId']
        print(f'Successfully published message with ID: {message_id}')
    except ClientError:
        print('Unable to publish message.')

    return {'statusCode': 200}
