import os, re
from functools import partial

import markup, metadata
from funcutils import file_to_str, str_to_file, pipe, atr, fmap, ffilter, lcompose
from miscutils import logger

log = logger()


def post_file_to_post_data(post_filename, static_filenames, template):
    """ Make post data """

    post_str = file_to_str(post_filename)
    title, raw_body, raw_metadata = split_post_metadata(post_str)
    body_html = markup.to_html(raw_body)
    metadata_data = metadata.raw_metadata_to_datadict(raw_metadata)
    metadata_html = metadata.datadict_to_html(metadata_data)
    post_data = {
        'body_html': body_html,
        'metadata_html': metadata_html,
        'metadata': metadata_data,
        'title': title,
        'filename': post_filename.split('/')[-1][:-4]  # remove mandatory .txt,
        }
    post_html = make_html_page(template, static_filenames, post_data)
    return post_data, post_html


def split_post_metadata(raw_post):
    """ Take post text, return raw post and raw metadata """

    title, _, rest = raw_post.partition('\n')
    result = re.split(r'~{3,}', rest)
    result_len = len(result)
    assert result_len < 3, 'Invalid markup'
    if len(result) == 1:
        return (title, result[0], '')
    elif len(result) == 2:
        return (title, result[0], result[1])


def make_html_page(template, static_filenames, post_data):
    """ Create HTML file """

    return pipe(template,
                [file_to_str,
                 atr('split', '\n'),
                 fmap(atr('strip')),
                 '\n'.join,
                 atr('format', **{
                        'css_filename': static_filenames['primary_css'],
                        'dark_css_filename': static_filenames['dark_css'],
                        'javascript': static_filenames['js'],
                        'site_name': 'Site Name',
                        'page_title': post_data['title'],
                        'body': post_data['body_html'],
                        'metadata': post_data['metadata_html'],
                        })
                 ])
