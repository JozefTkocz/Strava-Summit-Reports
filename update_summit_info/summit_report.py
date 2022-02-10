import pandas as pd

from update_summit_info.hill_classification import PRIMARY_CLASSIFICATIONS, \
    PRIMARY_TOP_CLASSIFICATIONS, HEIRARCHICAL_CLASSIFICATIONS


def generate_visited_summit_report(reported_classifications, summits_to_report):
    hill_info_strings = generate_hill_data_strings(summits_to_report, reported_classifications)
    return generate_report(hill_info_strings)


def generate_hill_data_strings(hill_report_data, reported_classifications):
    df = pd.DataFrame(columns=PRIMARY_CLASSIFICATIONS + PRIMARY_TOP_CLASSIFICATIONS + HEIRARCHICAL_CLASSIFICATIONS.to_list())
    for idx, rc in reported_classifications.items():
        df.loc[idx, :] = False
        df.loc[idx, rc] = True
    hill_info_strings = {}
    for classification in df.columns:
        hills = df.loc[df[classification]].index

        if hills.any():
            info_strings = []
            for hill in hills:
                info_strings.append(generate_hill_info_string(hill, hill_report_data))
            hill_info_strings.update({classification + 's': ', '.join(info_strings)})
    return hill_info_strings


def generate_report(hill_info):
    if not len(hill_info):
        return None

    report = 'Summits visited:\n\n'
    for classification, info in hill_info.items():
        report += classification + ':\n'
        report += info + '\n\n'

    return report


def generate_hill_info_string(hill_id, hill_data):
    name = hill_data.loc[hill_id, 'Name']
    height = hill_data.loc[hill_id, 'Metres']
    return f'{name} ({height} m)'