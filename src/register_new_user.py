import logging
import json

from lambda_helpers.strava_client import create_strava_client_from_env

from typing import Dict, Union


def lambda_handler(event, context):
    strava_client = create_strava_client_from_env()
    lambda_url = 'a_url'

    authorisation_code = parse_code_from_query_string(event)

    if authorisation_code is None:
        scope = 'read_all,activity:read_all,activity:write'
        code_request_url = strava_client.authorisation.generate_authorisation_url(scope=scope,
                                                                                  redirect_uri=lambda_url)
        return {'statusCode': 400,
                'body': json.dumps({'Authorisation url': code_request_url})}
    else:
        try:
            athlete_id = strava_client.authorisation.authorise_athlete(authorisation_code)
            return {'statusCode': 200,
                    'body': json.dumps(f'Successfully registered athlete with ID {athlete_id}')}
        except:
            logging.exception('Unable to authorise athlete')
            return {'statusCode': 400,
                    'body': json.dumps(f'Unable to register athlete.')}


def parse_code_from_query_string(event: Dict) -> Union[int, None]:
    queryStringParameters = event.get('queryStringParameters')
    if queryStringParameters is not None:
        challenge = queryStringParameters.get('code')
    else:
        challenge = None
    return challenge