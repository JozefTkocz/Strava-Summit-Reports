import pandas as pd
import numpy as np
from typing import Dict, List, Union

from summits.report_configuration import ReportConfiguration


def generate_summit_report(summits: pd.DataFrame, config: ReportConfiguration) -> str:
    classification_codes = config.code_mapping
    summit_classifications = get_summit_classifications(summits=summits,
                                                        classification_columns=list(classification_codes.keys()))
    summit_classifications = convert_classification_codes_to_names(summit_classifications, mapping=classification_codes)
    reduced_classifications = reduce_classification_list(summit_classifications=summit_classifications,
                                                         report_configuration=config)

    return generate_visited_summit_report(summits, reduced_classifications, config=config)


def get_summit_classifications(summits: pd.DataFrame,
                               classification_columns: List[str]) -> Dict[str, List[str]]:
    """
    Given a table of summits, return a dictionary where the keys are summit ID and the values are a list of
    corresponding applicable summit classifications

    :param summits: pd.DataFrame representing a database of summits
    :param classification_columns: A list of column names. The columns should be Boolean flags denoting whether a given
    summit belongs to the corresponding classification (values denoting True/False are 0/1 respectively).
    :return: A dictionary where the key is the database index, and the value is a list of corresponding classifications
    """
    columns_present = [c for c in summits.columns if c in classification_columns]
    df = (summits[columns_present] == 1).T

    summit_classification_codes = {}
    for summit in df.columns:
        classification_series = df[summit]
        classifications = classification_series.loc[classification_series].index.to_list()
        summit_classification_codes.update({summit: classifications})

    return summit_classification_codes


def convert_classification_codes_to_names(summit_classifications: Dict[str, List[str]],
                                          mapping: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Given a dictionary of summits and their classification codes, apply the mapping to the classification codes to
    return a dictionary of summits and their classification names.

    :param summit_classifications: Dict where keys are summit identifiers, and values are lists of corresponding summit
    classification codes
    :param mapping: Dict defining a mapping between classification codes and classification names
    :return: Dict where keys are summit identifiers, and values are corresponding classification names
    """
    for idx, codes in summit_classifications.items():
        long_names = []
        for c in codes:
            long_name = mapping.get(c)
            if long_name is not None:
                long_names.append(long_name)

        summit_classifications.update({idx: long_names})
    return summit_classifications


def reduce_classification_list(summit_classifications: Dict[str, List[str]],
                               report_configuration: ReportConfiguration) -> Dict[str, List[str]]:
    """
    Take a dictionary defining the applicable summit classifications for a set of summits, and omit summit
    classifications according to the specification given in ReportConfiguration. The reduction is performed as follows:
        - Primary summit types are always reported. Primary summits can be multiply reported if a summit belongs to more
        than one primary summit classification.
        - Primary tops are reported, only if they are not themselves also primary summits. Primary tops can be multiply
        reported if a summit belongs to more than one primary top classification.
        - If a summit is neither primary, nor a primary top, it is reported once, with its highest-ranked classification.

    :param summit_classifications: Dicionary, where keys are summit names, and values are a list of corresponding summit
    classification names
    :param report_configuration: ReportConfiguration object defining how summit classes are prioritised for reporting
    :return: Dictionary where keys are summit names, and values are summit classification names, reduced according to
    the configuration object
    """
    reported_classifications = {}
    primary_classifications = report_configuration.primary_classifications
    primary_top_classifications = report_configuration.primary_top_classifications

    for summit_name, summit_types in summit_classifications.items():
        final_summit_types = []
        secondary_classification = None
        highest_rank = 0

        is_primary_summit = np.any([t in primary_classifications for t in summit_types])
        is_primary_top = np.any([t in primary_top_classifications for t in summit_types])

        for summit_type in summit_types:
            if is_primary_summit and summit_type in primary_classifications:
                # always report primary summits, even if duplicated
                final_summit_types.append(summit_type)

            if is_primary_top and not is_primary_summit and summit_type in primary_top_classifications:
                # only report tops if they're not already primary summits
                final_summit_types.append(summit_type)

            if not (is_primary_summit or is_primary_top):
                # Only report secondary summit types in their highest-ranked classification
                rank = report_configuration.get_rank(summit_type)
                if rank is not None and rank >= highest_rank:
                    highest_rank = rank
                    secondary_classification = summit_type

        if secondary_classification is not None:
            final_summit_types.append(secondary_classification)

        reported_classifications.update({summit_name: final_summit_types})

    return reported_classifications


def generate_visited_summit_report(summits_database_table: pd.DataFrame,
                                   visited_summit_classifications: Dict[str, List[str]],
                                   config: ReportConfiguration) -> str:
    """
    Given a reference database table of summits, including 'Name' and 'Height' columns, and dictionary of visited
    summits and the corresponding classifications they are to be reported under, and a ReportConfiguration object
    defining which summit classifications are reported, and their reporting order, generate a summary report o the
    visited summits.

    :param summits_database_table: pd.DataFrame of summit data, inlcuding 'Name' and 'Height' columns
    :param visited_summit_classifications: dictionary mapping summit IDs to the summit classifications they are to be
    reported under
    :param config: ReportConfig object defining the reported summit classifications, and their reporting order.
    :return: string summary report for the visited summits
    """
    report_strings_by_classification = get_summit_descriptions_by_classification(summits_database_table,
                                                                                 visited_summit_classifications,
                                                                                 config)
    return generate_report_from_classification_descriptions(report_strings_by_classification)


def get_summit_descriptions_by_classification(hill_report_data: pd.DataFrame,
                                              reported_classifications: Dict[str, List[str]],
                                              config: ReportConfiguration) -> Dict[str, str]:
    """
    Given a table of summit information (including 'Name' and 'Height' columns), and a dictionary mapping summit names
    to the classifications they are to be reported under, and a ReportConfiguration object defining the summit
    classifications that are to be reported, and their reporting order, generate a dictionary of summit descriptions
    for each classification to be reported

    :param hill_report_data: pd.DataFrame containing summit information, including 'Name' amd 'Metres' columns
    :param reported_classifications: Dictionary mapping each summit name to the classifications it is to be reported
    under
    :param config: ReportConfiguration class defining the summit classifications that are reported, and their report
    order
    :return: Dictionary of summit classifications and their corresponding summit descriptions.
    """
    # Make a table of Boolean flags denoting whether a summit belongs to each classification in the report
    summit_classes = pd.DataFrame(columns=config.code_mapping.values())
    for idx, (summit_name, reported_classes) in enumerate(reported_classifications.items()):
        summit_classes.loc[idx, :] = False
        summit_classes.loc[idx, reported_classes] = True

    summit_descriptions = {}
    for classification in summit_classes.columns:
        summits_of_class = summit_classes.loc[summit_classes[classification]].index
        if summits_of_class.any():
            descriptions_for_class = []
            for summit in summits_of_class:
                descriptions_for_class.append(generate_summit_description(summit, hill_report_data))
            summit_descriptions.update({str(classification) + 's': ', '.join(descriptions_for_class)})
    return summit_descriptions


def generate_report_from_classification_descriptions(classification_reports: Dict[str, str]) -> Union[str, None]:
    """
    Given a dictionary of summit classifications and corresponding summit report summaries, produce a final report
    detailing summit information across all classifications.

    :param classification_reports: dictionary where keys are summit classifications, and values are the
    corresponding summary reports for each classification.
    :return: string containing complete summary report
    """
    if not len(classification_reports):
        return None

    report = 'Summits visited:\n'
    for classification, sub_report in classification_reports.items():
        report += classification + ': '
        report += sub_report + '\n\n'

    return report[:-2]


def generate_summit_description(hill_id: int, hill_data: pd.DataFrame) -> str:
    """
    Given a pd.DataFrame containing 'Name' and 'Metres' columns, and an index value, create a short summary string
    describing the summit at that index. The string should be formatted as '<name> <height> m'.

    :param hill_id: index of the targeted database entry
    :param hill_data: database of summit data, including 'Name' and 'Height' columns
    :return: a string describing the summit corresponding to the chosen index.
    """
    name = hill_data.loc[hill_id, 'Name']
    height = hill_data.loc[hill_id, 'Metres']
    return f'{name} ({height} m)'
