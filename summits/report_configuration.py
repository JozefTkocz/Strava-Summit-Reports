from dataclasses import dataclass
from typing import List, Union

import pandas as pd


@dataclass
class ReportedSummit:
    code: str
    name: str
    is_primary: bool
    is_top: bool


class ReportConfiguration:
    def __init__(self, summit_classes: List[ReportedSummit]):
        self.classes = summit_classes
        self.highest_classification_rank = self.secondary_classification_ranking.index.max()

    def get_rank(self, class_name: str) -> Union[int, None]:
        rank = self.secondary_classification_ranking.loc[
            self.secondary_classification_ranking == class_name].index.values
        if len(rank):
            return rank[0]
        else:
            return None

    @property
    def primary_classifications(self) -> List[str]:
        return [c.name for c in self.classes if c.is_primary and not c.is_top]

    @property
    def primary_top_classifications(self) -> List[str]:
        return [c.name for c in self.classes if c.is_primary and c.is_top]

    @property
    def secondary_classification_ranking(self) -> pd.Series:
        return pd.Series(reversed([c.name for c in self.classes if not c.is_primary]))

    @property
    def code_mapping(self):
        return {c.code: c.name for c in self.classes}


REPORT_CONFIG = ReportConfiguration([
    # Primary classifications -always report, even if duplicated
    ReportedSummit(code='M', name='Munro', is_primary=True, is_top=False),
    ReportedSummit(code='C', name='Corbett', is_primary=True, is_top=False),
    ReportedSummit(code='G', name='Graham', is_primary=True, is_top=False),
    ReportedSummit(code='D', name='Donald', is_primary=True, is_top=False),
    ReportedSummit(code='F', name='Furth', is_primary=True, is_top=False),
    ReportedSummit(code='W', name='Wainwright', is_primary=True, is_top=False),
    # Tops -only report if not already primary
    ReportedSummit(code='MT', name='Munro Top', is_primary=True, is_top=True),
    ReportedSummit(code='CT', name='Corbett Top', is_primary=True, is_top=True),
    ReportedSummit(code='GT', name='Graham Top', is_primary=True, is_top=True),
    ReportedSummit(code='DT', name='Donald Top', is_primary=True, is_top=True),
    # Secondary classifications - only report once, according to highest ranked class
    ReportedSummit(code='Hew', name='Hewitt', is_primary=False, is_top=False),
    ReportedSummit(code='N', name='Nutall', is_primary=False, is_top=False),
    ReportedSummit(code='Ma', name='Marilyn', is_primary=False, is_top=False),
    ReportedSummit(code='Hu', name='Hump', is_primary=False, is_top=False),
    ReportedSummit(code='Tu', name='Tump', is_primary=False, is_top=False),
    ReportedSummit(code='Sim', name='Simm', is_primary=False, is_top=False)
])

