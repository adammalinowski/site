import os
import sys
import traceback

import funcutils as fu
import html
import markup
import metadata
from miscutils import nice_date


def make_404(output_dir, static_filenames):
    title = '404 Error - File not found'
    body_html = html.data_to_html_post({
        'title': title,
        'body_html': 'Not to worry, why not <a href="/">have a look around</a>?',
        'date': '',
    })
    page_html = html.data_to_html_page(static_filenames, title, body_html)
    fu.str_to_file(output_dir + '404.html', page_html)


def make_page(publish, input_dir, output_dir, static_filenames, filename):
    """ Take in dir & filename, make & output HTML. Return post data"""

    post_str = fu.file_to_str(input_dir + filename)
    url_filename = html.urlize(filename[:-4])  # remove .txt, make url
    post_output_filename = url_filename + '.html'
    source_output_filename = url_filename + '.txt'
    title, raw_body, raw_metadata = html.split_post_metadata(
        post_str,
        require_metadata=publish,
    )
    raw_body, tags = markup.inline_tag_thing(raw_body)
    typed_chunks = markup.post_to_typed_chunks(raw_body)
    body_html = markup.typed_chunks_to_html_page(typed_chunks)
    toc_list = markup.typed_chunks_to_toc_list(typed_chunks)
    if toc_list:
        toc_html = 'Page contents:\n' + markup.toc_list_to_toc(toc_list)
    else:
        toc_html = ''
    metadata_data = metadata.raw_metadata_to_datadict(raw_metadata)
    metadata_data['source'] = source_output_filename
    post_data = {
        'body_html': body_html,
        'date': nice_date(metadata_data['date']),
        'metadata': metadata_data,
        'title': title,
        'filename': post_output_filename,
        'toc': toc_html,
        'footer': True,
    }
    content = html.data_to_html_post(post_data)
    post_html = html.data_to_html_page(
        static_filenames,
        title,
        content,
    )
    fu.str_to_file(output_dir + post_output_filename, post_html)
    fu.str_to_file(output_dir + source_output_filename, post_str)
    return post_data


def all_posts_html(post_datas):
    """ Make html list of all posts for homepage """

    entries = [
        markup.link(
            post_data['filename'],
            post_data['title'],
        ) +
        markup.tagify('div', post_data['date'], clss='date')
        for post_data in post_datas
    ]
    return ''.join(markup.tagify('div', e, clss='entry') for e in entries)


def make_posts(publish, post_source_dir, output_dir, static_filenames):

    post_filenames = [
        filename for filename in os.listdir(post_source_dir)
        if filename.endswith('.txt')
    ]
    post_datas = []
    for filename in post_filenames:
        try:
            post_data = make_page(
                publish,
                post_source_dir,
                output_dir,
                static_filenames,
                filename,
            )
        except Exception as e:
            if publish:
                raise e
            # otherwise just print the error and continue to next post
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print('Make page failed for {0} with {1}'.format(filename, e))
            traceback.print_exc()
            print('\n')
        else:
            post_datas.append(post_data)
    return post_datas


def make_homepage(output_dir, static_filenames, post_datas):
    """ Make the homepage as list of links to other pages """

    sorted_post_data = sorted(
        post_datas,
        reverse=True,
        key=lambda pd: pd['metadata']['date'],
    )
    body_html = all_posts_html(sorted_post_data)
    homepage_html = html.data_to_html_page(
        static_filenames,
        'adammalinowski.co.uk',
        body_html,
    )
    fu.str_to_file(output_dir + 'index.html', homepage_html)
