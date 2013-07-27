import os
import argparse
import logging
from functools import partial

import simples3

# package stuff
import conf
import assets
import html
import markup
import metadata

# package utils
from funcutils import file_to_str, str_to_file, lcompose, ffilter, atr, pmap, pipe


""" Get filename of posts for conversion """
post_filenames = lcompose([
    os.listdir,
    ffilter(atr('endswith', '.txt')),
    ])


def raw_body_to_html(raw_body):
    """ just for testing but need proper abstraction """

    raw_body, tags = markup.inline_tag_thing(raw_body)
    typed_chunks = markup.post_to_typed_chunks(raw_body)
    body_html = markup.typed_chunks_to_html_page(typed_chunks)
    return body_html


def make_page(input_dir, output_dir, post_data_to_html_page, filename):
    """ Take in dir & filename, make html & output. Return post data"""

    post_str = file_to_str(input_dir + filename)
    source_output_filename = html.urlize(filename)
    post_output_filename = source_output_filename[:-4] + '.html' # .txt -> .html
    title, raw_body, raw_metadata = html.split_post_metadata(post_str)
    raw_body, tags = markup.inline_tag_thing(raw_body)
    typed_chunks = markup.post_to_typed_chunks(raw_body)
    body_html = markup.typed_chunks_to_html_page(typed_chunks)
    toc_list = markup.typed_chunks_to_toc_list(typed_chunks)
    if toc_list:
        toc_html = 'Contents:\n' +  markup.toc_list_to_toc(toc_list)
    else:
        toc_html = ''
    metadata_data = metadata.raw_metadata_to_datadict(raw_metadata)
    metadata_data['source'] = source_output_filename
    metadata_html = metadata.datadict_to_html(metadata_data)
    post_data = {
        'body_html': body_html,
        'metadata_html': metadata_html,
        'metadata': metadata_data,
        'title': title,
        'filename': post_output_filename,
        'toc': toc_html,
        }
    post_html = post_data_to_html_page(post_data)
    str_to_file(output_dir + post_output_filename, post_html)
    str_to_file(output_dir + source_output_filename, post_str)
    return post_data


def simple_post_data(body_html, title):
    return {
        'title': title,
        'body_html': body_html,
        'metadata_html': "",
        'toc': "",
    }


def make_homepage(output_dir, post_data_to_html_page, post_datas):
    """ Make the homepage as list of links to other pages """

    sorted_post_data = sorted(post_datas, reverse=True,
                              key=lambda pd: pd['metadata']['date'])
    homepage_post_str = "All posts, most recent first:\n\n"
    homepage_post_str += '\n'.join(
        '<a href="{0}">{1}</a>'.format(post_data['filename'], post_data['title'])
        for post_data in sorted_post_data)
    body_html = pipe(homepage_post_str, [markup.post_to_typed_chunks,
                                         markup.typed_chunks_to_html_page])
    post_html = post_data_to_html_page(simple_post_data(body_html, 'Home'))
    str_to_file(output_dir + 'home.html', post_html)


def make_404(output_dir, post_data_to_html_page):
    post_data = simple_post_data('Feel free to have a look around though.', '404 Error - File not found')
    post_html = post_data_to_html_page(post_data)
    str_to_file(output_dir + '404.html', post_html)


def main(opts):
    """ Build the site """

    static_filenames = make_static_assets(opts)
    template = html.clean_template(opts['template'])
    post_data_to_html_page = partial(html.data_to_html_page,
                                     *(template, static_filenames))
    post_datas = pmap(make_page,
                      (opts['post_in'], opts['site_out'], post_data_to_html_page),
                      post_filenames(opts['post_in']))
    make_homepage(opts['site_out'], post_data_to_html_page, post_datas)
    make_404(opts['site_out'], post_data_to_html_page)


def make_static_assets(opts):
    """ Make css & js files, return dict of filenames """

    css_filename, dark_css_filename = do_css(opts['css_in'], opts['site_out'])
    js_filename = do_js(opts['js_in'], opts['site_out'])
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
    dark_css_str = file_to_str(css_input_dir + 'dark.css')
    dark_css_name = assets.get_cachebusting_name(dark_css_str) + '.css'

    # remove and write
    assets.remove_extention('.css', css_output_dir)
    str_to_file(css_output_dir + css_name, css_str)
    str_to_file(css_output_dir + dark_css_name, dark_css_str)

    return css_name, dark_css_name


def do_js(js_input_dir, js_output_dir):
    """ Take input js, combine, cachebust, replace existing output """

    assets.remove_extention('.js', js_output_dir)
    js_str = assets.get_js(js_input_dir)
    js_name = assets.get_cachebusting_name(js_str) + '.js'
    str_to_file(js_output_dir + js_name, js_str)
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
    parser.add_argument("--verbosity",
                        type=int,
                        choices=[0, 1, 2],
                        default=0,
                        help="choose verbosity; 0 = None, 1 = Some, 2 = All")
    subparsers = parser.add_subparsers(help='sub-command help')

    # make the output sub-command parser
    parser_output = subparsers.add_parser('output',
                        help="output either publish posts or draft posts")
    parser_output.add_argument('output',
                   choices=['publish', 'draft', 'upload'],
                   default='publish',
                   help="choose 'publish' or 'draft' posts to output locally "
                        "or upload to upload to live web site")

    # make the test post sub-command parser
    parser_test = subparsers.add_parser('test', help='tranform test input as raw body to html')
    parser_test.add_argument('input',
                             help="input test input")

    return vars(parser.parse_args())


def init_s3():
    access_key = os.environ['S3_ACCESS_KEY_ID']
    secret_key = os.environ['S3_SECRET_ACCESS_KEY']
    bucket_name = 'adammalinowski.co.uk'
    base_url = 'https://' + bucket_name + '.s3.amazonaws.com'
    s3 = simples3.S3Bucket(bucket_name,
                           access_key=access_key,
                           secret_key=secret_key,
                           base_url=base_url)
    return s3


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


def upload(site_dir):
    s3 = init_s3()
    for filename in os.listdir(site_dir):
        s3.put(filename, file_to_str(site_dir + filename),
               mimetype=filename_to_mimetype(filename),
               headers=filename_to_headers(filename))


if __name__ == "__main__":
    """ Use command line args and config to do the business """

    args = get_args()
    #configure_logging(args['verbosity'])
    if args.get('test'):
        print raw_body_to_html(args['test'])
    else:
        pub = args['output'] in ['publish', 'upload']
        site_dir = conf.PUBLISH_OUTPUT_DIR if pub else conf.DRAFT_OUTPUT_DIR
        opts = {
            'css_in': conf.CSS_INPUT_DIR,
            'css_out': conf.CSS_INPUT_DIR,
            'js_in': conf.JS_INPUT_DIR,
            'js_in': conf.JS_INPUT_DIR,
            'post_in': conf.POST_INPUT_DIR if pub else conf.DRAFT_INPUT_DIR,
            'site_out': site_dir,
            'template': '/projects/site/templates/base.html',
        }
        main(opts)
        print 'output done'
        if args['output'] == 'upload':
            upload(site_dir)
            print 'upload done'