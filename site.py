import os
import argparse
import logging
from functools import partial

# package stuff
import assets
import html
import markup

# package utils
from miscutils import get_cachebusting_name
from funcutils import file_to_str, str_to_file, lcompose, ffilter, atr, pmap


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
HOME = os.path.expanduser("~")
POST_INPUT_DIR = HOME + '/posts/publish/'
DRAFT_INPUT_DIR = HOME + '/posts/drafts/'
PUBLISH_OUTPUT_DIR = HOME + '/posts/publish_output/'
DRAFT_OUTPUT_DIR = HOME + '/posts/drafts_output/'
CSS_INPUT_DIR = PROJECT_ROOT + '/css/'
JS_INPUT_DIR = PROJECT_ROOT + '/js/'


""" Get filename of posts for conversion """
post_filenames = lcompose([
    os.listdir,
    ffilter(atr('endswith', '.txt')),
    ])


def make_page(input_dir, output_dir, post_data_to_html_page, filename):
    """ Take in dir & filename, make html & output. Return post data"""

    post_full_path = input_dir + filename
    post_str = file_to_str(post_full_filename)
    post_data = html.post_file_to_post_data(post_str)
    post_html = post_data_to_html_page(post_data)
    output_filename = post_filename[:-4]  # remove mandatory .txt,
    str_to_file(output_dir + output_filename, post_html)
    return post_data


def make_homepage(output_dir, post_data_to_html_page, post_datas):
    """ Make the homepage as list of links to other pages """

    sorted_post_data = sorted(post_datas, reverse=True
                              key=lambda pd: pd['metadata']['date'])
    homepage_post_str = '\n'.join(
        '<a href="{0}">{1}</a>'.format(post_data['filename'], post_data['title'])
        for post_data in sorted_post_data)
    post_data = {
        'body_html': markup.to_html(homepage_post_str),
        'metadata_html': "",
        'title': "Home",
    }
    post_html = post_data_to_html_page(post_data)
    str_to_file(output_dir + 'home', post_html)


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
    css_name = get_cachebusting_name(css_str) + '.css'

    # dark css
    dark_css_str = file_to_str(css_input_dir + 'dark.css')
    dark_css_name = get_cachebusting_name(dark_css_str) + '.css'

    # remove and write
    assets.remove_extention('.css', css_output_dir)
    str_to_file(css_output_dir + css_name, css_str)
    str_to_file(css_output_dir + dark_css_name, dark_css_str)

    return css_name, dark_css_name


def do_js(js_input_dir, js_output_dir):
    """ Take input js, combine, cachebust, replace existing output """

    assets.remove_extention('.js', js_output_dir)
    js_str = assets.get_js(js_input_dir)
    js_name = get_cachebusting_name(js_str) + '.js'
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


if __name__ == "__main__":
    """ Take command line arg of whether to publish draft or real, do it """

    parser = argparse.ArgumentParser()
    parser.add_argument("output",
                        choices=['publish', 'draft'],
                        help="either publish or output drafts")
    parser.add_argument("-v", "--verbosity",
                        type=int,
                        choices=[0, 1, 2],
                        help="choose verbosity; 0 = None, 1 = Some, 2 = All")
    parsed_args = parser.parse_args()
    publish = parsed_args.output == 'publish'
    verbosity = parsed_args.verbosity
    opts = {
        'css_in': CSS_INPUT_DIR,
        'css_out': CSS_INPUT_DIR,
        'js_in': JS_INPUT_DIR,
        'js_in': JS_INPUT_DIR,
        'post_in': POST_INPUT_DIR if publish else DRAFT_INPUT_DIR,
        'site_out': PUBLISH_OUTPUT_DIR if publish else DRAFT_OUTPUT_DIR,
        'template': '/projects/site/templates/base.html',
    }
    configure_logging(verbosity)
    main(opts)
    print 'done'
