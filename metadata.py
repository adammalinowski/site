import re

from funcutils import file_to_str, str_to_file, lcompose, atr, fmap, ffilter
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


def raw_dict_to_data_dict(metadata):
    """ Convert metadata string input to data according to type """

    metadata_funcs = {
        'date': str,
        'tags': lambda tag_str: tag_str.split(',')
        }
    return dict((k, metadata_funcs[k](v)) for k, v in metadata.items()
                if k in metadata_funcs)


def data_dict_to_html(metadata_data):
    """ Convert metadata data to html """

    html_list = []
    if 'date' in metadata_data:
        date_html = '<span id="date">%s</span>' % metadata_data['date']
        html_list.append(date_html)
    if 'tags' in metadata_data and False:
        tag_links = ['<a href="/tags/{tag_str}/">{tag_str}</a>'\
                     .format(tag_str=tag_str.strip())
                     for tag_str in metadata_data['tags']]
        tag_html = '<span id="tags">%s</span>' % ' '.join(tag_links)
        html_list.append(tag_html)
    return ''.join(html_list)


""" Convert raw metdata to html """
to_html = lcompose([
    raw_metadata_to_raw_dict,
    raw_dict_to_data_dict,
    data_dict_to_html,
    ])
