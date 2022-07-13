import pandas as pd

from summits.summit_report import get_summit_classifications, convert_classification_codes_to_names, \
    reduce_classification_list, ReportedSummit, ReportConfiguration
from summits.report_config import REPORT_CONFIG


def test_get_summit_classifications():
    example_summits_df = pd.DataFrame({'class_1': [0, 0, 1],
                                       'class_2': [0, 1, 1],
                                       'class_3': [1, 1, 1]}, index=['summit_a', 'summit_b', 'summit_c'])
    expected_result = {'summit_a': ['class_3'],
                       'summit_b': ['class_2', 'class_3'],
                       'summit_c': ['class_1', 'class_2', 'class_3']}
    calculated_result = get_summit_classifications(summits=example_summits_df,
                                                   classification_columns=['class_1', 'class_2', 'class_3'])
    assert calculated_result == expected_result


def test_get_summit_classifications_include_classification_not_present_in_database():
    example_summits_df = pd.DataFrame({'class_1': [0, 0, 1],
                                       'class_2': [0, 1, 1],
                                       'class_3': [1, 1, 1]}, index=['summit_a', 'summit_b', 'summit_c'])
    expected_result = {'summit_a': ['class_3'],
                       'summit_b': ['class_2', 'class_3'],
                       'summit_c': ['class_1', 'class_2', 'class_3']}
    calculated_result = get_summit_classifications(summits=example_summits_df,
                                                   classification_columns=['class_1', 'class_2', 'class_3',
                                                                           'unrepresented_class'])
    assert calculated_result == expected_result


def test_convert_classification_codes_to_names():
    code_mapping = {'a': 'summit_type_a',
                    'b': 'summit_type_b',
                    'c': 'summit_type_c'}
    summit_classifications = {'summit_1': ['a'],
                              'summit_2': ['a', 'b'],
                              'summit_3': []}

    expected_result = {'summit_1': ['summit_type_a'],
                       'summit_2': ['summit_type_a', 'summit_type_b'],
                       'summit_3': []}
    calculated_result = convert_classification_codes_to_names(summit_classifications=summit_classifications,
                                                              mapping=code_mapping)
    assert calculated_result == expected_result


def test_reduce_classifications_list_extracts_primary_summits_and_primary_tops():
    summit_classifications = {'summit_1': ['Munro', 'Munro Top'],
                              'summit_2': ['Munro Top', 'Tump', 'Hump'],
                              'summit_3': ['Hump', 'Tump'],
                              'summit_4': ['Tump']}

    munro = ReportedSummit(code='M', name='Munro', is_primary=True, is_top=False)
    munro_top = ReportedSummit(code='MT', name='Munro Top', is_primary=True, is_top=True)
    hump = ReportedSummit(code='H', name='Hump', is_primary=False, is_top=False)
    tump = ReportedSummit(code='T', name='Tump', is_primary=False, is_top=False)

    report_config = ReportConfiguration([munro, munro_top, hump, tump])

    expected_result = {'summit_1': ['Munro'],
                       'summit_2': ['Munro Top'],
                       'summit_3': ['Hump'],
                       'summit_4': ['Tump']}
    calculated_result = reduce_classification_list(summit_classifications, report_config)
    assert calculated_result == expected_result


def test_reduce_classification_list_with_multiply_classified_tops():
    donald = ReportedSummit(code='D', name='Donald', is_primary=True, is_top=False)
    donald_top = ReportedSummit(code='DT', name='Donald Top', is_primary=True, is_top=True)
    graham_top = ReportedSummit(code='GT', name='Graham Top', is_primary=True, is_top=True)
    graham = ReportedSummit(code='G', name='Graham', is_primary=True, is_top=False)
    tump = ReportedSummit(code='Tu', name='Tump', is_primary=False, is_top=False)
    sim = ReportedSummit(code='Sm', name='Sim', is_primary=False, is_top=False)

    input_data = {"King's Seat Hill": ['Tump', 'Donald', 'Graham Top', 'Donald Top'],
                  "Tarmangie Hill": ['Tump', 'Donald', 'Graham Top'],
                  "Innerdownie": ['Tump', 'Donald', 'Graham Top'],
                  "Whitewisp Hill": ['Tump', 'Donald Top', 'Graham Top'],
                  "Cairnmorris Hill": ['Sim', 'Tump', 'non-configured-hill']}

    report_config = ReportConfiguration([graham, donald, graham_top, donald_top, tump, sim])
    calculated_result = reduce_classification_list(input_data, report_config)
    expected_result = {"King's Seat Hill": ['Donald'],
                       "Tarmangie Hill": ['Donald'],
                       "Innerdownie": ['Donald'],
                       "Whitewisp Hill": ['Graham Top', 'Donald Top'],
                       "Cairnmorris Hill": ['Tump']}

    # list order is not important, sort lists in returned dict
    def sort_dict(dictionary):
        return {key: sorted(value) for key, value in dictionary.items()}

    assert sort_dict(calculated_result) == sort_dict(expected_result)


def test_reduce_classification_list_with_configuration():
    report_config = REPORT_CONFIG
    input_data = {"King's Seat Hill": ['Tump', 'Donald', 'Graham Top', 'Donald Top'],
                  "Tarmangie Hill": ['Tump', 'Donald', 'Graham Top'],
                  "Innerdownie": ['Tump', 'Donald', 'Graham Top'],
                  "Whitewisp Hill": ['Tump', 'Donald Top', 'Graham Top'],
                  "Cairnmorris Hill": ['Sim', 'Tump', 'non-configured-hill']}

    calculated_result = reduce_classification_list(input_data, report_config)
    expected_result = {"King's Seat Hill": ['Donald'],
                       "Tarmangie Hill": ['Donald'],
                       "Innerdownie": ['Donald'],
                       "Whitewisp Hill": ['Graham Top', 'Donald Top'],
                       "Cairnmorris Hill": ['Tump']}

    # list order is not important, sort lists in returned dict
    def sort_dict(dictionary):
        return {key: sorted(value) for key, value in dictionary.items()}

    assert sort_dict(calculated_result) == sort_dict(expected_result)
