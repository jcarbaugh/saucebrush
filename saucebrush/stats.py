from saucebrush.filters import Filter
import itertools
import math

def _average(values):
    """ Calculate the average of a list of values.
    
        :param values: an iterable of ints or floats to average
    """
    return sum(values) / float(len(values))

def _median(values):
    """ Calculate the median of a list of values.
    
        :param values: an iterable of ints or floats to calculate
    """
    
    count = len(values)
    
    # bail early before sorting if 0 or 1 values in list
    if count == 0:
        return None
    elif count == 1:
        return values[0]
    
    values = sorted(values)
    
    if count % 2 == 1:
        # odd number of items, return middle value
        return float(values[count / 2])
    else:
        # even number of items, return average of middle two items
        mid = count / 2
        return sum(values[mid - 1:mid + 1]) / 2.0

def _stddev(values, population=False):
    """ Calculate the standard deviation and variance of a list of values.
    
        :param values: an iterable of ints or floats to calculate
        :param population: True if values represents entire population,
            False if it is a sample of the population
    """
    
    avg = _average(values)
    count = len(values) if population else len(values) - 1
    
    # square the difference between each value and the average
    diffsq = ((i - avg) ** 2 for i in values)
    
    # the average of the squared differences
    variance = sum(diffsq) / float(count)
    
    return (math.sqrt(variance), variance) # stddev is sqrt of variance

class StatsFilter(Filter):
    """ Base for all stats filters.
    """
    
    def __init__(self, field, test=None):
        self._field = field
        self._test = test
        
    def process_record(self, record):
        if self._test is None or self._test(record):
            self.process_field(record[self._field])
        return record
    
    def process_field(self, record):
        raise NotImplementedError('process_field not defined in ' +
                                  self.__class__.__name__)
    
    def value(self):
        raise NotImplementedError('value not defined in ' +
                                  self.__class__.__name__)

class Sum(StatsFilter):
    """ Calculate the sum of the values in a field. Field must contain either
        int or float values.
    """
    
    def __init__(self, field, initial=0, **kwargs):
        super(Sum, self).__init__(field, **kwargs)
        self._value = initial
        
    def process_field(self, item):
        self._value += item or 0
        
    def value(self):
        return self._value

class Average(StatsFilter):
    """ Calculate the average (mean) of the values in a field. Field must
        contain either int or float values.
    """
    
    def __init__(self, field, initial=0, **kwargs):
        super(Average, self).__init__(field, **kwargs)
        self._value = initial
        self._count = 0
        
    def process_field(self, item):
        if item is not None:
            self._value += item
            self._count += 1
        
    def value(self):
        return self._value / float(self._count)

class Median(StatsFilter):
    """ Calculate the median of the values in a field. Field must contain
        either int or float values.
        
        **This filter keeps a list of field values in memory.**
    """
    
    def __init__(self, field, **kwargs):
        super(Median, self).__init__(field, **kwargs)
        self._values = []
    
    def process_field(self, item):
        if item is not None:
            self._values.append(item)
    
    def value(self):
        return _median(self._values)

class MinMax(StatsFilter):
    """ Find the minimum and maximum values in a field. Field must contain
        either int or float values.
    """
    
    def __init__(self, field, **kwargs):
        super(MinMax, self).__init__(field, **kwargs)
        self._max = None
        self._min = None
    
    def process_field(self, item):
        if item is not None:
            if self._max is None or item > self._max:
                self._max = item
            if self._min is None or item < self._min:
                self._min = item
    
    def value(self):
        return (self._min, self._max)

class StandardDeviation(StatsFilter):
    """ Calculate the standard deviation of the values in a field. Calling
        value() will return a standard deviation for the sample. Pass
        population=True to value() for the standard deviation of the
        population. Convenience methods are provided for average() and
        median(). Field must contain either int or float values.

        **This filter keeps a list of field values in memory.**
    """
    
    def __init__(self, field, **kwargs):
        super(StandardDeviation, self).__init__(field, **kwargs)
        self._values = []
    
    def process_field(self, item):
        if item is not None:
            self._values.append(item)
    
    def average(self):
        return _average(self._values)
    
    def median(self):
        return _median(self._values)
    
    def value(self, population=False):
        """ Return a tuple of (standard_deviation, variance).
            
            :param population: True if values represents entire population,
                False if values is a sample. Default: False
        """
        return _stddev(self._values, population)