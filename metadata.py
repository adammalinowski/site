import re
import datetime

from funcutils import file_to_str, str_to_file, lcompose, atr, fmap, ffilter, args
from miscutils import logger

log = logger()


def lower_dict_keys(adict):
    return dict((k.lower(), v) for k, v in adict.items())


""" Convert raw metadatas to dict of key -> val """
raw_metadata_to_raw_dict = lcompose([
    atr('split', '\n'),
    ffilter(None),
    fmap(atr('split', ':')),
    dict,
    lower_dict_keys,
    ])


""" Take a date string like 2013/06/13, return date object """
date_str_to_date = lcompose([
    atr('strip'),
    atr('split', '/'),
    fmap(int),
    args(datetime.date)
    ])


def raw_dict_to_datadict(metadata):
    """ Convert metadata string input to data according to type """

    metadata_funcs = {
        'date': date_str_to_date,
        'tags': lambda tag_str: tag_str.split(',')
        }
    return dict((k, metadata_funcs[k](v)) for k, v in metadata.items()
                if k in metadata_funcs)


def datadict_to_html(metadata_data):
    """ Convert metadata data to html """

    html_list = []

    assert 'date' in metadata_data, 'Missing date'
    date_html = '<span>%s</span>' % metadata_data['date']
    html_list.append(date_html)

    source_html = '<span><a href="%s">source</a></span>' % metadata_data['source']
    html_list.append(source_html)

    return ' '.join(html_list)


raw_metadata_to_datadict = lcompose([
    raw_metadata_to_raw_dict,
    raw_dict_to_datadict])
