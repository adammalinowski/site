import os, re
from functools import partial

import markup, metadata
from funcutils import file_to_str, str_to_file, pipe, atr, fmap, ffilter, lcompose
from miscutils import logger

log = logger(0)


# todo: xotd
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
    title, raw_body, raw_metadata = split_post_metadata(post_str)
    html_file_name = filename[:-4]  # remove mandatory .txt
    body_html = markup.to_html(raw_body)
    metadata_html = metadata.to_html(raw_metadata)
    template = '/projects/site/templates/base.html'
    post_html = make_html_page(template, body_html, metadata_html, css_filename, title)
    str_to_file(html_output_dir + html_file_name, post_html)


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
def make_html_page(template, body_html, metadata_html, css_filename, title):
    """ Create HTML file """

    return pipe(template,
                [file_to_str,
                 atr('split', '\n'),
                 fmap(atr('strip')),
                 '\n'.join,
                 atr('format', **{
                        'css_filename': css_filename,
                        'site_name': 'Site Name',
                        'page_title': title,
                        'body': body_html,
                        'metadata': metadata_html,
                        })
                 ])
