import datetime

import funcutils as fu
from miscutils import logger

log = logger()


def lower_dict_keys(adict):
    return dict((k.lower(), v) for k, v in adict.items())


""" Convert raw metadatas to dict of key -> val """
raw_metadata_to_raw_dict = fu.lcompose([
    fu.atr('split', '\n'),
    fu.ffilter(None),
    fu.fmap(fu.atr('split', ':')),
    dict,
    lower_dict_keys,
])


""" Take a date string like 2013/06/13, return date object """
date_str_to_date = fu.lcompose([
    fu.atr('strip'),
    fu.atr('split', '/'),
    fu.fmap(int),
    fu.args(datetime.date)
])


def raw_dict_to_datadict(metadata):
    """ Convert metadata string input to data according to type """

    metadata_funcs = {
        'date': date_str_to_date,
        'category': fu.lcompose([str.strip, str.lower]),
    }
    return dict((k, metadata_funcs[k](v)) for k, v in metadata.items()
                if k in metadata_funcs)


raw_metadata_to_datadict = fu.lcompose([
    raw_metadata_to_raw_dict,
    raw_dict_to_datadict
])
