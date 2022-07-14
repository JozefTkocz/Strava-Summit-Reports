import json
import pandas as pd
from unittest import mock
import os

from src.weather.report import generate_weather_report_for_activity

TEST_DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'data')


def mock_get_weather_data(*args, **kwargs) -> pd.DataFrame:
    df = pd.read_csv(os.path.join(TEST_DATA_DIRECTORY, 'weather.csv'))
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df['condition'] = df['condition'].apply(lambda x: x.replace('\'', '"'))
    df['condition'] = df['condition'].apply(lambda x: json.loads(x))
    return df


@mock.patch('src.weather.report.get_weather_history', side_effect=mock_get_weather_data)
def test_generate_weather_report_for_activity(mock_get_weather):
    with open(os.path.join(TEST_DATA_DIRECTORY, 'activity.json'), 'r') as file:
        activity = json.load(file)

    calculated_result = generate_weather_report_for_activity(api_key='my_key', strava_activity=activity)
    expected_result = ('Weather: Patchy rain possible\n'
                       'Temperature: 7.9 °C (feels like 3.7 °C)\n'
                       'Wind (mph): 11.8, gusting 24.8')
    assert calculated_result == expected_result
