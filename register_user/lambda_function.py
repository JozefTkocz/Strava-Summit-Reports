import os

from stravaclient import DynamoDBCache, StravaClient, OAuthHandler


def lambda_handler(event, context):
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    region_name = os.environ.get('region_name')
    table_name = os.environ.get('table_name')

    print('Connecting to authentication token database...')
    token_cache = DynamoDBCache(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name,
                                table_name=table_name)

    query_string_parameters = event.get('queryStringParameters')
    if query_string_parameters is not None:
        code = query_string_parameters.get('code')
        scope = query_string_parameters.get('scope')
    else:
        code = None
        scope = None

    if code is not None and scope is not None:
        pass
        # check no error
        # upsert token to store
        # return success message

    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    strava_authorisation = OAuthHandler(client_id=client_id,
                                        client_secret=client_secret,
                                        token_cache=token_cache)

    strava_authorisation.prompt_user_authorisation()

    print('Executed successfully')
    return {'statusCode': 200}


if __name__ == '__main__':
    lambda_handler('a', 'b')
