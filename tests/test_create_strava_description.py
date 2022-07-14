from update_strava_description import create_strava_description


def test_create_strava_description_all_reports_populated():
    input_data = ['A', 'B', 'C']
    expected_result = 'A\n\nB\n\nC'
    calculated_result = create_strava_description(input_data)
    assert calculated_result == expected_result


def test_create_strava_description_some_reports_null():
    input_data = ['A', None, 'C']
    expected_result = 'A\n\nC'
    calculated_result = create_strava_description(input_data)
    assert calculated_result == expected_result


def test_create_strava_description_all_reports_null():
    input_data = [None, None, None]
    expected_result = None
    calculated_result = create_strava_description(input_data)
    assert calculated_result == expected_result
