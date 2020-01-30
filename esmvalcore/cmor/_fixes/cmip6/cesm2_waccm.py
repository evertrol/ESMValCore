"""Fixes for CESM2-WACCM model."""
from .cesm2 import Tas as BaseTas
from ..cmip5.bcc_csm1_1 import Cl as BaseCl


class Cl(BaseCl):
    """Fixes for cl."""


class Tas(BaseTas):
    """Fixes for tas."""
