import numpy as np
import pandas as pd

CLASSIFICATION_COLUMNS = ['Ma', 'Ma=', 'Hu', 'Hu=', 'Tu', 'Sim', '5', 'M', 'MT', 'F', 'C', 'G', 'D', 'DT', 'Hew', 'N',
                          'Dew',
                          'DDew', 'HF', '4', '3', '2', '1', '0', 'W', 'WO', 'B', 'Sy', 'Fel', 'CoH', 'CoH=', 'CoU',
                          'CoU=', 'CoA', 'CoA=', 'CoL', 'CoL=', 'SIB', 'sMa', 'sHu', 'sSim', 's5', 's4', 'Mur', 'CT',
                          'GT', 'BL', 'Bg', 'Y', 'Cm', 'T100', 'xMT', 'xC', 'xG', 'xN', 'xDT', 'Dil', 'VL', 'A', 'Ca',
                          'Bin', 'O', 'Un']
CLASSIFICATION_CODES = {
    'M': 'Munro',
    'MT': 'Munro Top',
    'C': 'Corbett',
    'CT': 'Corbett Top',
    'G': 'Graham',
    'GT': 'Graham Top',
    'D': 'Donald',
    'DT': 'Donald Top',
    'Ma': 'Marilyn',
    'Hu': 'Hump',
    'Tu': 'Tump',
    'Sim': 'Simm',
    'Hew': 'Hewitt',
    'N': 'Nutall',
    'W': 'Wainwright,'
}

PRIMARY_CLASSIFICATIONS = ['Munro', 'Corbett', 'Graham', 'Donald', 'Furth', 'Wainwright']
PRIMARY_TOP_CLASSIFICATIONS = ['Munro Top', 'Corbett Top', 'Graham Top', 'Donald Top']
HEIRARCHICAL_CLASSIFICATIONS = pd.Series(data={
    1: 'Hewitt',
    2: 'Nutall',
    3: 'Marilyn',
    4: 'Hump',
    5: 'Tump',
})


def reduce_classification_list(hill_classification_codes):
    last = {}

    for idx, codes in hill_classification_codes.items():
        final_codes = []
        highest_rank = HEIRARCHICAL_CLASSIFICATIONS.index.max()

        is_primary = np.any([c in PRIMARY_CLASSIFICATIONS for c in codes])
        is_primary_top = np.any([c in PRIMARY_TOP_CLASSIFICATIONS for c in codes])

        for c in codes:
            if is_primary and c in PRIMARY_CLASSIFICATIONS:
                final_codes.append(c)

            if is_primary_top and not is_primary and c in PRIMARY_TOP_CLASSIFICATIONS:
                final_codes.append(c)

            if not (is_primary or is_primary_top):
                rank = HEIRARCHICAL_CLASSIFICATIONS.loc[HEIRARCHICAL_CLASSIFICATIONS == c].index.values
                if len(rank):
                    rank = rank[0]

                    if rank <= highest_rank:
                        highest_rank = rank
                        final_codes.append(c)

        last.update({idx: final_codes})

    return last


def convert_classification_codes_to_names(hill_classification_codes):
    for idx, codes in hill_classification_codes.items():
        long_names = []
        for c in codes:
            long_name = CLASSIFICATION_CODES.get(c)
            if long_name is not None:
                long_names.append(long_name)

        hill_classification_codes.update({idx: long_names})
    return hill_classification_codes


def get_hill_classification_codes(hill_report_data):
    df = (hill_report_data[CLASSIFICATION_COLUMNS] == 1).T

    hill_classification_codes = {}
    for hill in df.columns:
        classification_series = df[hill]
        classifications = classification_series.loc[classification_series == True].index.to_list()
        hill_classification_codes.update({hill: classifications})

    return hill_classification_codes


def get_report_summit_classifications(summits_to_report):
    hill_classification_codes = get_hill_classification_codes(summits_to_report)
    hill_classifications = convert_classification_codes_to_names(hill_classification_codes)
    reported_classifications = reduce_classification_list(hill_classifications)
    return reported_classifications
