import json

import numpy as np
import pandas as pd

from update_summit_info.hill_classification import CLASSIFICATION_COLUMNS, get_report_summit_classifications
from update_summit_info.hill_location import get_candidate_summits_from_local_maxima, filter_visited_summits
from update_summit_info.summit_report import generate_visited_summit_report


def lambda_handler(event, context):
    with open('streamset.json', 'r') as file:
        data = json.load(file)

    route_data = parse_streams_dataframe(data)
    summits = get_candidate_summits_from_local_maxima(route_data)
    hills_database = pd.read_csv('./DoBIH_v17_3.csv', index_col=0)
    db = hills_database[['Name', 'Latitude', 'Longitude', 'Metres', 'Classification'] + CLASSIFICATION_COLUMNS]

    summits_to_report = filter_visited_summits(db, summits)
    reported_classifications = get_report_summit_classifications(summits_to_report)
    report = generate_visited_summit_report(reported_classifications, summits_to_report)
    print(report)

    # Update the strava status
    print('Executed successfully')
    return {'statusCode': 200}


def parse_streams_dataframe(streams_json):
    lat = np.array(streams_json['latlng']['data'])[:, 0]
    lng = np.array(streams_json['latlng']['data'])[:, 1]
    columns = streams_json.keys()
    df = pd.DataFrame()
    for col in columns:
        df[col] = streams_json[col]['data']
    df['lat'] = lat
    df['lng'] = lng
    return df


if __name__ == '__main__':
    result = lambda_handler('a', 'b')
