from src.process_strava_webhook import is_unsubscription_event

import json
import os

TEST_DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def test_is_unsubscription_event_with_update_to_unsubscribe_athlete():
    example_unsubscription_event = os.path.join(TEST_DATA_DIRECTORY, 'unsubscription_event.json')
    with open(example_unsubscription_event, 'r') as file:
        event = json.load(file)

    expected_result = True
    calculated_result = is_unsubscription_event(event)
    assert calculated_result == expected_result


def test_is_unsubscription_event_with_activity_update_event():
    example_unsubscription_event = os.path.join(TEST_DATA_DIRECTORY, 'activity_update_event.json')
    with open(example_unsubscription_event, 'r') as file:
        event = json.load(file)

    expected_result = False
    calculated_result = is_unsubscription_event(event)
    assert calculated_result == expected_result
