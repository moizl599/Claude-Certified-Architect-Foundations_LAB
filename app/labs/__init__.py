"""Aggregate all lab content into a single list."""

from labs.domain1 import LABS as D1
from labs.domain2 import LABS as D2
from labs.domain3 import LABS as D3
from labs.domain4 import LABS as D4
from labs.domain5 import LABS as D5

ALL_LABS = D1 + D2 + D3 + D4 + D5
