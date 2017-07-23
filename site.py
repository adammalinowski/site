import argparse
import datetime
import logging
import os
import sys
import traceback
from functools import partial

from boto import s3
from boto.s3.connection import OrdinaryCallingFormat

# package stuff
import conf
import assets
import html
import markup
import metadata

# package utils
import funcutils as fu
from miscutils import nice_date


def get_post_filenames(post_source_dir):
    """ Get filenames of posts for conversion """

    composed = fu.lcompose([
        os.listdir,
        fu.ffilter(fu.atr('endswith', '.txt')),
    ])
    return composed(post_source_dir)


def raw_body_to_html(raw_body):
    """ just for testing but need proper abstraction """

    raw_body, tags = markup.inline_tag_thing(raw_body)
    typed_chunks = markup.post_to_typed_chunks(raw_body)
    body_html = markup.typed_chunks_to_html_page(typed_chunks)
    return body_html


def make_page(opts, post_data_to_html_page, filename):
    """ Take in dir & filename, make & output HTML. Return post data"""

    input_dir, output_dir = opts['post_source_dir'], opts['out_dir']
    post_str = fu.file_to_str(input_dir + filename)
    url_filename = html.urlize(filename[:-4])  # remove .txt, make url
    post_output_filename = url_filename + '.html'
    source_output_filename = url_filename + '.txt'
    title, raw_body, raw_metadata = html.split_post_metadata(
        post_str,
        require_metadata=opts['publish'],
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
    post_html = post_data_to_html_page(post_data)
    fu.str_to_file(output_dir + post_output_filename, post_html)
    fu.str_to_file(output_dir + source_output_filename, post_str)
    return post_data


def try_make_page(opts, post_data_to_html_page, filename):
    try:
        return make_page(opts, post_data_to_html_page, filename)
    except(Exception, e):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print('Make page failed for {0} with {1}'.format(filename, e))
        traceback.print_exc()
        print('\n')


def simple_post_data(body_html, title, **kwargs):
    data = {
        'title': title,
        'body_html': body_html,
        'metadata_html': "",
        'toc': "",
        'footer': True,
        'date': '',
    }
    data.update(kwargs)
    return data


def page_list(post_datas):
    return '\n'.join(
        markup.link(
            post_data['filename'],
            post_data['title'],
        )
        for post_data in post_datas
    )


def make_homepage(output_dir, post_data_to_html_page, post_datas):
    """ Make the homepage as list of links to other pages """

    sorted_post_data = sorted(
        post_datas,
        reverse=True,
        key=lambda pd: pd['metadata']['date'],
    )
    category_post_data = fu.seq_to_group_dict(
        sorted_post_data,
        lambda pd: pd['metadata']['category'],
    )
    homepage_post_str = ''
    for category in ['posts', 'ideas', 'notes']:
        post_datas = category_post_data[category]
        homepage_post_str += (
            '<h3>' + category.title() + '</h3>' + page_list(post_datas)
        )

    body_html = fu.pipe(
        homepage_post_str,
        [markup.post_to_typed_chunks, markup.typed_chunks_to_html_page],
    )
    post_html = post_data_to_html_page(
        simple_post_data(
            body_html,
            '',
        )
    )
    fu.str_to_file(output_dir + 'index.html', post_html)


def make_404(output_dir, post_data_to_html_page):
    post_data = simple_post_data(
        'Feel free to have a look around though.',
        '404 Error - File not found',
    )
    post_html = post_data_to_html_page(post_data)
    fu.str_to_file(output_dir + '404.html', post_html)


def make_site(opts):
    static_filenames = make_static_assets(opts)
    template = html.clean_file(opts['template'])

    # partially apply apart from post data
    post_data_to_html_page = partial(
        html.data_to_html_page,
        *(template, static_filenames)
    )

    if opts['publish']:
        make_page_func = make_page
    else:
        make_page_func = try_make_page

    post_filenames = get_post_filenames(opts['post_source_dir'])
    thing = partial(make_page_func, *(opts, post_data_to_html_page))
    post_datas = map(thing, post_filenames)
    post_datas = filter(None, post_datas)  # try_make_page may return None

    make_homepage(opts['out_dir'], post_data_to_html_page, post_datas)
    make_404(opts['out_dir'], post_data_to_html_page)


def make_static_assets(opts):
    """ Make cachebusted css & js files, return dict of filenames """

    css_filename, dark_css_filename = do_css(
        opts['css_source_dir'],
        opts['out_dir'],
    )
    js_filename = do_js(
        opts['js_source_dir'],
        opts['out_dir'],
    )
    return {
        'primary_css': css_filename,
        'dark_css': dark_css_filename,
        'js': js_filename
    }


def do_css(css_input_dir, css_output_dir):
    """ Take input css & dark css, combine, cachebust, replace """

    # primary css
    css_str = assets.combine_css(css_input_dir)
    css_name = assets.get_cachebusting_name(css_str) + '.css'

    # dark css
    dark_css_str = fu.file_to_str(css_input_dir + 'dark.css')
    dark_css_name = assets.get_cachebusting_name(dark_css_str) + '.css'

    # remove and write
    assets.remove_extention('.css', css_output_dir)
    fu.str_to_file(css_output_dir + css_name, css_str)
    fu.str_to_file(css_output_dir + dark_css_name, dark_css_str)

    return css_name, dark_css_name


def do_js(js_input_dir, js_output_dir):
    """ Take input js, combine, cachebust, replace existing output """

    assets.remove_extention('.js', js_output_dir)
    js_str = assets.get_js(js_input_dir)
    js_name = assets.get_cachebusting_name(js_str) + '.js'
    fu.str_to_file(js_output_dir + js_name, js_str)
    return js_name


def configure_logging(level):
    """ Set up the logger with level from command line arg """

    logger = logging.getLogger("logger")
    if level == 0:
        logger.setLevel(logging.WARNING)
    elif level == 1:
        logger.setLevel(logging.INFO)
    elif level == 2:
        logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


def get_args():
    """ Get publish True/False and verbosity from command line args

    subparsers see

    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=0,
        help="choose verbosity; 0 = None, 1 = Some, 2 = All",
    )
    subparsers = parser.add_subparsers(help='sub-command help')

    # make the output sub-command parser
    parser_output = subparsers.add_parser(
        'output',
        help="output either publish posts or draft posts",
    )
    parser_output.add_argument(
        'output',
        choices=['publish', 'draft', 'upload'],
        default='publish',
        help="choose 'publish' or 'draft' posts to output locally "
             "or upload to upload to live web site",
    )

    # make the test post sub-command parser
    parser_test = subparsers.add_parser(
        'test',
        help='tranform test input as raw body to html',
    )
    parser_test.add_argument(
        'input',
        help="input test input",
    )

    return vars(parser.parse_args())


def get_s3_bucket():
    conn = s3.connect_to_region(
        'eu-west-2',
        aws_access_key_id=os.environ['S3_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['S3_SECRET_ACCESS_KEY'],
        is_secure=True,
    )
    return conn.get_bucket('adammalinowski')


def extension(filename):
    splitfilename = filename.split('.')
    return splitfilename[-1] if len(splitfilename) > 1 else 'html'


def filename_to_mimetype(filename):
    extension_to_mimetype = {
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'text/javascript',
    }
    return extension_to_mimetype[extension(filename)]


def filename_to_headers(filename):
    no_cache = {'Cache-Control': 'private, max-age=0'}
    long_cache = {'Cache-Control': 'public, max-age=31449600'}
    extension_to_headers = {
        'txt': no_cache,
        'html': no_cache,
        'css': long_cache,
        'js': long_cache,
    }
    return extension_to_headers[extension(filename)]


def upload(out_dir):
    bucket = get_s3_bucket()
    for file_name in os.listdir(out_dir):
        file_path = out_dir + file_name
        content_type = filename_to_mimetype(file_name)
        key = s3.key.Key(bucket)
        key.key = file_name
        key.content_type = content_type
        headers = filename_to_headers(file_name)
        print('putting', file_name)
        key.set_contents_from_filename(
            file_path,
            headers=headers,
        )
        key.make_public()


def get_options():
    args = get_args()
    # configure_logging(args['verbosity'])

    if args.get('test'):
        print(raw_body_to_html(args['test']))
        return

    publish = args['output'] in ['publish', 'upload']  # draft if false
    out_dir = conf.PUBLISH_OUTPUT_DIR if publish else conf.DRAFT_OUTPUT_DIR
    post_source_dir = conf.POST_INPUT_DIR if publish else conf.DRAFT_INPUT_DIR
    options = {
        'publish': publish,
        'css_source_dir': conf.CSS_INPUT_DIR,
        'css_out': conf.CSS_INPUT_DIR,
        'js_source_dir': conf.JS_INPUT_DIR,
        'post_source_dir': post_source_dir,
        'out_dir': out_dir,
        'template': conf.PROJECT_ROOT + '/templates/base.html',
        'upload': args['output'] == 'upload',
    }
    return options


def main():
    """ Use command line args and config to do the business """

    options = get_options()
    make_site(options)
    print('output done ' + datetime.datetime.now().strftime('%H:%M:%S'))

    if options['upload']:
        upload(options['out_dir'])
        print('upload done')


if __name__ == "__main__":
    main()
