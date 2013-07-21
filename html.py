import os, re
from functools import partial

from funcutils import file_to_str, str_to_file, pipe, atr, fmap, ffilter, lcompose
from miscutils import logger

log = logger()


def split_post_metadata(raw_post):
    """ Take raw post text, return title, raw post and raw metadata """

    title, _, rest = raw_post.partition('\n')
    result = re.split(r'~{3,}', rest)
    assert len(result) == 2, 'Invalid markup'
    return (title, result[0], result[1])


clean_template = lcompose([
    file_to_str,
    atr('split', '\n'),
    fmap(atr('strip')),
    '\n'.join,
    ])


def data_to_html_page(template, static_filenames, post_data):
    """ Put it all together into HTML page """
    return template.format(**{
                'css_filename': static_filenames['primary_css'],
                'dark_css_filename': static_filenames['dark_css'],
                'javascript': static_filenames['js'],
                'site_name': 'Site Name',
                'page_title': post_data['title'],
                'body': post_data['body_html'],
                'metadata': post_data['metadata_html'],
                'toc': post_data['toc'],
                })


def urlize(astr):
    """ Turn string into slug suitable to be url """
    return astr.replace(' ', '_').lower()
