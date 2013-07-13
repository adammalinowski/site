import os
import argparse

import assets, html, markup

from miscutils import get_cachebusting_name
from funcutils import file_to_str, str_to_file, lcompose, ffilter, atr, pmap


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
HOME = os.path.expanduser("~")
POST_INPUT_DIR = HOME + '/posts/publish/'
DRAFT_INPUT_DIR = HOME + '/posts/drafts/'
PUBLISH_OUTPUT_DIR = HOME + '/posts/output/'
DRAFT_OUTPUT_DIR = HOME + '/posts/output_drafts/'
CSS_INPUT_DIR = PROJECT_ROOT + '/css/'
JS_INPUT_DIR = PROJECT_ROOT + '/js/'


""" Get filename of posts for conversion """
post_filenames = lcompose([
    os.listdir,
    ffilter(atr('endswith', '.txt')),
    ])


def make_page(input_dir, output_dir, static_filenames, filename):
    """ Take in dir & filename, make html & output. Return filename & title """

    html_file_name, post_html, title =\
        html.postfile_to_html(input_dir + filename, static_filenames)
    str_to_file(output_dir + html_file_name, post_html)
    return (html_file_name, title)


def make_homepage(output_dir, static_filenames, files_with_titles):
    """ Make the homepage as list of links to other pages """

    # need to order by date and refactor
    homepage_post_str = '\n'.join('<a href="{0}">{1}</a>'.format(*file_title)
                                  for file_title in files_with_titles)
    body_html = markup.to_html(homepage_post_str)
    template = '/projects/site/templates/base.html'
    post_html = html.make_html_page(template, body_html, "", static_filenames,
                                    'Home')
    str_to_file(output_dir + 'home', post_html)


def main(dirs):
    """ Build the site """

    static_filenames = make_static_assets(dirs)
    files_with_titles = pmap(make_page,
                             (dirs['post_in'], dirs['site_out'], static_filenames),
                             post_filenames(dirs['post_in']))
    make_homepage(dirs['site_out'], static_filenames, files_with_titles)


def make_static_assets(dirs):
    css_filename, dark_css_filename = do_css(dirs)
    js_filename = do_js(dirs)
    return {
        'primary_css': css_filename,
        'dark_css': dark_css_filename,
        'js': js_filename
    }


def do_css(dirs):
    """ Take input css & dark css, combine, cachebust, replace """

    css_input_dir, css_output_dir = dirs['css_in'], dirs['site_out']

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


def do_js(dirs):
    """ Take input js, combine, cachebust, replace existing output """

    js_input_dir, js_output_dir = dirs['js_in'], dirs['site_out']
    js_str = assets.get_js(js_input_dir)
    js_name = get_cachebusting_name(js_str) + '.js'
    assets.remove_extention('.js', js_output_dir)
    str_to_file(js_output_dir + js_name, js_str)
    return js_name


if __name__ == "__main__":
    """ Take command line arg of whether to publish draft or real, do it """

    parser = argparse.ArgumentParser()
    parser.add_argument("output", choices=['publish', 'draft'],
                        help="either publish or output drafts")
    parsed_args = parser.parse_args()
    publish = parsed_args.output == 'publish'
    dirs = {
        'css_in': CSS_INPUT_DIR,
        'css_out': CSS_INPUT_DIR,
        'js_in': JS_INPUT_DIR,
        'js_in': JS_INPUT_DIR,
        'post_in': POST_INPUT_DIR if publish else DRAFT_INPUT_DIR,
        'site_out': PUBLISH_OUTPUT_DIR if publish else DRAFT_OUTPUT_DIR,
    }
    main(dirs)
