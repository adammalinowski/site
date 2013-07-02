import os, re
from functools import partial

import markup, metadata
from funcutils import file_to_str, str_to_file, pipe, atr, fmap, ffilter, lcompose
from miscutils import logger

log = logger(0)


"""
todo:
- markup
    - lists
    - quotes (inner & block)
    - optional line breaking
- general
    - warnings:
        - trailing char after link e.g. http:example.com,
    - homepage
    - handling for un-publishing?
"""


@log
def do_html(html_input_dir, html_output_dir, css_filename):
    for filename in post_filenames(html_input_dir):
        file_thing(html_input_dir, html_output_dir, css_filename, filename)


""" Get filename of posts for conversion """
post_filenames = lcompose([
    os.listdir,
    ffilter(atr('endswith', '.txt')),
    ])


@log
def file_thing(html_input_dir, html_output_dir, css_filename, filename):
    post_str = file_to_str(html_input_dir + filename)
    raw_body, raw_metadata = split_post_metadata(post_str)
    html_file_name = filename[:-4]  # remove mandatory .txt
    body_html = markup.to_html(raw_body)
    metadata_html = metadata.to_html(raw_metadata)
    post_html = make_html_page(body_html, metadata_html, css_filename)
    str_to_file(html_output_dir + html_file_name, post_html)


def split_post_metadata(raw_post):
    """ Take post text, return raw post and raw metadata """
    result = re.split(r'~{3,}', raw_post)
    result_len = len(result)
    assert result_len < 3, 'Invalid markup'
    if len(result) == 1:
        return (result[0], '')
    elif len(result) == 2:
        return result


@log
def make_html_page(body_html, metadata_html, css_filename):
    """ Create HTML file """
    return pipe('/projects/stat/templates/base.html',
                [file_to_str,
                 atr('split', '\n'),
                 fmap(atr('strip')),
                 '\n'.join,
                 atr('format', **{
                        'css_filename': css_filename,
                        'site_name': 'Site Name',
                        'page_title': 'hello',
                        'body': body_html,
                        'metadata': metadata_html,
                        })
                 ])
