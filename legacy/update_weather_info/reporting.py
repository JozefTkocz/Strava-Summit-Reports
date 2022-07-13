from typing import Union

import pandas as pd


def construct_weather_summary_string(df, start_time, end_time):
    start = pd.to_datetime(start_time).floor('1H')
    end = pd.to_datetime(end_time).ceil('1H')
    data = df.loc[(df.index >= start) & (df.index <= end)]
    degree_symbol = u'\N{DEGREE SIGN}'

    condition = data['condition'].mode().iloc[0]['text']
    temperature = data['temp_c'].mean()
    feels_like = data['feelslike_c'].min()
    windspeed = data['wind_mph'].mean()
    gust = data['gust_mph'].max()

    summary = (f"Weather: {condition}\n"
               f"Temperature: {temperature:.1f} {degree_symbol}C (feels like {feels_like:.1f} {degree_symbol}C)\n"
               f"Wind (mph): {windspeed:.1f}, gusting {gust:.1f}")

    return summary


def generate_strava_activity_report(weather_report: Union[str, None],
                                    summit_report: Union[str, None]) -> Union[str, None]:
    report = ''
    if summit_report is not None:
        report = summit_report

    if len(report) and (weather_report is not None):
        print('Adding newlines...')
        report += '\n\n'

    if weather_report is not None:
        report += weather_report

    if len(report):
        return report
    else:
        return None