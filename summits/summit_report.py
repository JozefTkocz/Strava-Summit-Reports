import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class ReportedSummit:
    code: str
    name: str
    is_primary: bool
    is_top: bool


class ReportConfiguration:
    def __init__(self, summit_classes: List[ReportedSummit]):
        self.classes = summit_classes
        self.primary_classifications = self.primary_classifications()
        self.primary_top_classifications = self.primary_top_classifications()
        self.secondary_classification_ranking = self.secondary_classification_ranking()
        self.highest_classification_rank = self.secondary_classification_ranking.index.max()

    def get_rank(self, class_name: str) -> Union[int, None]:
        rank = self.secondary_classification_ranking.loc[
            self.secondary_classification_ranking == class_name].index.values
        if len(rank):
            return rank[0]
        else:
            return None

    def primary_classifications(self) -> List[str]:
        return [c.name for c in self.classes if c.is_primary and not c.is_top]

    def primary_top_classifications(self) -> List[str]:
        return [c.name for c in self.classes if c.is_primary and c.is_top]

    def secondary_classification_ranking(self) -> pd.Series:
        return pd.Series(reversed([c.name for c in self.classes if not c.is_primary]))


def generate_summit_report(summits: pd.DataFrame) -> str:
    summit_classifications = get_summit_classifications(summits=summits,
                                                        classification_columns=list(CLASSIFICATION_CODES.keys()))
    summit_classifications = convert_classification_codes_to_names(summit_classifications, mapping=CLASSIFICATION_CODES)

    return 'no'


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
        print(classification_series)
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
