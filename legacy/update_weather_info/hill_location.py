from typing import Union

import numpy as np
import pandas as pd
from peak_finder import detect_peaks


def haversine_distance(lon1: Union[np.array, float],
                       lat1: Union[np.array, float],
                       lon2: Union[np.array, float],
                       lat2: Union[np.array, float]) -> Union[np.array, float]:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.square(np.sin(0.5 * dlat)) + np.cos(lat1) * np.cos(lat2) * np.square(np.sin(0.5 * dlon))
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000.


def find_nearest_summits(local_maxima: pd.DataFrame, hills_df: pd.DataFrame) -> pd.DataFrame:
    lat_peaks = np.radians(local_maxima['lat'].values)
    lng_peaks = np.radians(local_maxima['lng'].values)

    lat_hills = np.radians(hills_df['Latitude'].values)
    lng_hills = np.radians(hills_df['Longitude'].values)

    lat_peaks, lat_hills = np.meshgrid(lat_peaks, lat_hills, sparse=True)
    lng_peaks, lng_hills = np.meshgrid(lng_peaks, lng_hills, sparse=True)

    distance_matrix = haversine_distance(lng_hills, lat_hills, lng_peaks, lat_peaks)

    minimum_indices = np.argmin(distance_matrix, axis=0)
    distances = distance_matrix[minimum_indices, range(len(local_maxima))]

    return distances, minimum_indices


def get_candidate_summits_from_local_maxima(route_data):
    # do not low pass filter without scipy
    # route_data['alt_filtered'] = low_pass_filter(route_data['time'], route_data['altitude'])
    # do not use scipys peak finding algorithm without scipy
    # maxima, properties = signal.find_peaks(route_data['alt_filtered'].values)
    # This doesn't work well enough -not recommended to use
    maxima = detect_peaks(route_data['altitude'], mpd=10)
    route_data['max'] = False
    route_data.loc[maxima, 'max'] = True
    summits = route_data.loc[route_data['max']]
    return summits


def filter_visited_summits(db, peaks, distance_proximity=20):
    candidate_hills = get_hills_within_altitude_profile(db, peaks)
    candidate_hills = get_hills_within_latlng_grid(peaks=peaks, candidate_hills=candidate_hills, threshold_deg=0.1)
    nearest_hill_distance, nearest_hill_index = find_nearest_summits(peaks, candidate_hills)
    peaks.loc[:, 'named_hill_closest_distance'] = nearest_hill_distance
    peaks.loc[:, 'named_hill_index'] = nearest_hill_index
    hills_to_report = filter_visited_summits_by_proximity(peaks, distance_proximity)
    hill_report_data = candidate_hills.iloc[hills_to_report]
    return hill_report_data


def get_hills_within_latlng_grid(peaks, candidate_hills, threshold_deg=0.1):
    latlng_threshold = threshold_deg

    min_lat = peaks['lat'].min() - latlng_threshold
    max_lat = peaks['lat'].max() + latlng_threshold

    min_lng = peaks['lng'].min() - latlng_threshold
    max_lng = peaks['lng'].max() + latlng_threshold

    candidate_hills = candidate_hills.loc[
        (candidate_hills['Latitude'] > min_lat) & (candidate_hills['Latitude'] < max_lat)]
    candidate_hills = candidate_hills.loc[
        (candidate_hills['Longitude'] > min_lng) & (candidate_hills['Longitude'] < max_lng)]

    return candidate_hills


def get_hills_within_altitude_profile(db, peaks, height_threshold=50):
    max_search_height = peaks['altitude'].max() + height_threshold
    min_search_height = peaks['altitude'].min() - height_threshold
    candidate_hills = db.loc[(db['Metres'] > min_search_height) & (db['Metres'] < max_search_height)]
    return candidate_hills


def filter_visited_summits_by_proximity(peaks, threshold_distance=10):
    closest_points = pd.DataFrame(peaks.groupby('named_hill_index')['named_hill_closest_distance'].min())
    closest_points['is_within_threshold'] = closest_points['named_hill_closest_distance'] < threshold_distance
    # Pull out data for those visited hills
    hills_to_report = closest_points.loc[closest_points['is_within_threshold']].index
    return hills_to_report
