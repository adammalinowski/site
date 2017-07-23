import re
from functools import partial

import funcutils as fu
from miscutils import logger

log = logger()


def split_post_metadata(raw_post, require_metadata=False):
    """ Take raw post text, return title, raw post and raw metadata """

    title, _, rest = raw_post.partition('\n')
    result = re.split(r'~{3,}', rest)
    if len(result) == 1 and not require_metadata:
        result.append('Date: 1999/12/31')  # make fake metadata
    assert len(result) == 2, 'Invalid metadata markup'
    return (title, result[0], result[1])


def clean_file(path):
    """ Take filepath, remove unnecessary spaces """

    composed = fu.lcompose([
        fu.file_to_str,
        fu.atr('split', '\n'),
        fu.fmap(fu.atr('strip')),
        '\n'.join,
    ])
    return composed(path)


def data_to_html_page(template, static_filenames, post_data):
    """ Put it all together into HTML page """

    return template.format(
        css_filename=static_filenames['primary_css'],
        dark_css_filename=static_filenames['dark_css'],
        javascript_filename=static_filenames['js'],
        site_name='adammalinowski.co.uk',
        page_title=post_data['title'],
        body=post_data['body_html'],
        date=post_data['date'],
    )


""" Turn string into slug suitable to be url """
urlize = fu.lcompose([
    fu.atr('replace', ' ', '_'),
    fu.atr('lower'),
    partial(re.sub, *(r'[^\w-]', '',))
])
