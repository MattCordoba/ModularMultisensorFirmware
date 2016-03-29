__author__ = 'Matt Cordoba'
from enum import Enum
class PlotType(Enum):
    """
    Enumeration for different display views for the application end
    """
    TimeSeries = 1
    TimeSeriesMulti = 2
    TimeSeriesDigitalControl = 3