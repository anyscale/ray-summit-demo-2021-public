import datetime
import numpy as np
from dataclasses import dataclass


@dataclass
class Schema:
    author: str
    title: str
    content: str
    date: datetime.datetime
    label: str
    all_labels: tuple


@dataclass
class Data:
    x: np.array
    label: str
