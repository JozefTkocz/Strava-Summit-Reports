import numpy as np
import os

from data_sources.summits import LocalFileSummitReference
from models.coordinates import CoordinateSet
from summits.report_configuration import ReportConfiguration, REPORT_CONFIG
from summits.summit_report import generate_summit_report
from summits.visited_summits import find_visited_summits

MODULE_PATH = os.path.realpath(__file__)


def report_visited_summits(lat: np.array,
                           lng: np.array,
                           database_filepath) -> str:
    """
    Generate a summary report of summits visited

    :param lat: array of latitude coordinates
    :param lng: array of longitude coordinates
    :param database_filepath: path at which the hills database.pkl file is located
    :return: string visited summit report
    """
    reference_data_source = LocalFileSummitReference(filepath=database_filepath)
    gpx_trail = CoordinateSet(latitude=lat, longitude=lng)
    visited_summit_data = find_visited_summits(summit_reference_data=reference_data_source,
                                               gpx_trail=gpx_trail)
    return generate_summit_report(summits=visited_summit_data, config=REPORT_CONFIG)
