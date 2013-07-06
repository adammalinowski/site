import os, re
from functools import partial

import markup, metadata
from funcutils import file_to_str, str_to_file, pipe, atr, fmap, ffilter, lcompose
from miscutils import logger

log = logger(0)


@log
def postfile_to_html(post_filename, static_filenames):
    """ """
    post_str = file_to_str(post_filename)
    title, raw_body, raw_metadata = split_post_metadata(post_str)
    html_file_name = post_filename.split('/')[-1][:-4]  # remove mandatory .txt
    body_html = markup.to_html(raw_body)
    metadata_html = metadata.to_html(raw_metadata)
    template = '/projects/site/templates/base.html'
    post_html = make_html_page(template, body_html, metadata_html, static_filenames, title)
    return html_file_name, post_html


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


@log
def make_html_page(template, body_html, metadata_html, static_filenames, title):
    """ Create HTML file """

    return pipe(template,
                [file_to_str,
                 atr('split', '\n'),
                 fmap(atr('strip')),
                 '\n'.join,
                 atr('format', **{
                        'css_filename': static_filenames['primary_css'],
                        'dark_css_filename': static_filenames['dark_css'],
                        'site_name': 'Site Name',
                        'page_title': title,
                        'body': body_html,
                        'metadata': metadata_html,
                        'javascript': static_filenames['js'],
                        })
                 ])
