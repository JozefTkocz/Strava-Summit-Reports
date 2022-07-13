import os

from stravaclient import DynamoDBCache, StravaClient, OAuthHandler


def lambda_handler(event, context):
    aws_access_key_id = os.environ.get('aws_access_key_id')
    aws_secret_access_key = os.environ.get('aws_secret_access_key')
    region_name = os.environ.get('region_name')
    table_name = os.environ.get('table_name')

    aws_access_key_id = 'AKIA6H5DOJVE5OXPBX6N'
    aws_secret_access_key = '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'
    region_name = 'eu-west-2'
    table_name = 'StravaAuthTokens'


    print('Connecting to authentication token database...')
    token_cache = DynamoDBCache(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name,
                                table_name=table_name)

    query_string_parameters = None #event.get('queryStringParameters')
    if query_string_parameters is not None:
        code = query_string_parameters.get('code')
        scope = query_string_parameters.get('scope')
    else:
        code = None
        scope = None

    if code is not None and scope is not None:
        print('wur puppits')
        pass
        # check no error
        # upsert token to store
        # return success message

    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')

    client_id = 76410
    client_secret = 'acdd7307334f112810b24c3bd8491786f7c52293'

    strava_authorisation = OAuthHandler(client_id=client_id,
                                        client_secret=client_secret,
                                        token_cache=token_cache)

    strava_authorisation.prompt_user_authorisation()
    scope = 'read_all,activity:read_all,activity:write'
    redirect_uri = None
    authorisation_url = strava_authorisation.generate_authorisation_url(scope=scope, redirect_url=redirect_uri)

    print('Executed successfully')
    return {'statusCode': 200}


if __name__ == '__main__':
    lambda_handler('a', 'b')
